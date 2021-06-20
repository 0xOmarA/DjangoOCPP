from ocpp_lib.types import RemoteStartTransaction_Req
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
import logging, json, datetime
from ocpp_lib import call
from channels.db import database_sync_to_async

from ocpp_lib.enums import OCPPMessageType, OCPPCommands
from ocpp_lib.call import Call
from ocpp_lib.types import IdToken
from . import models as ocpp_models

# Initialize the logger
logger = logging.getLogger('ocpp')

class OcppConsumer(AsyncWebsocketConsumer):
    '''
    An OCPP consumer used to implement the OCPP 1.6J standard over websockets

    ## Description
    This consumer is the main consumer that the chargers connect to when they're 
    looking to send or receive OCPP commands. Contains the standard functions that
    any consumer needs.
    '''

    @database_sync_to_async
    def save_and_link_call_and_result(self, call_obj:ocpp_models.Call, call_result_obj:ocpp_models.CallResult) -> None:
        '''
        Saves the call and call result using async techniques.

        ## Description
        This method is created to take in a call and call result and save them.
        it will also perform the linkage needed for them.

        ## Parameters
        - `call_obj` (Call): The call object obtained from the models
        - `call_result_obj` (CallResult): The call result object obtained from the models
        '''
        # Saving them
        call_obj.save()
        call_result_obj.save()

        # Creating the linkage
        call_obj.call_result_obj = call_result_obj
        call_result_obj.call_obj = call_obj
        
        # Saving them
        call_obj.save()
        call_result_obj.save()

    async def connect(self):
        # Getting the charger ID from the URL that the charger 
        # visited
        self.charger_id = self.scope['url_route']['kwargs']['charger_id']
        self.charger_group = f'ocpp_{self.charger_id}'

        # Logging the visit
        logger.info(f"Charger with ID '{self.charger_id}' connected")

        # Making this charger join the room group
        await self.channel_layer.group_add(
            self.charger_group,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Logging the exit
        logger.info(f"Charger with ID '{self.charger_id}' disconnected")

        # Leave room group
        await self.channel_layer.group_discard(
            self.charger_group,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Deserializing the message sent.
        message = json.loads(text_data)
        logger.info(f"Received a message from '{self.charger_id}' of: {message}")

        # # Getting the message type id
        try:
            message_type_id = OCPPMessageType(message[0])
        except:
            logger.critical(f"Charger '{self.charger_id}' sent an unknown OCPP message type of {message[0]}")

        # Different action depending on the message tyep
        if message_type_id == OCPPMessageType.CALL:
            logger.info(f"Charger '{self.charger_id}' sent a Call message")
            
            # Loading the sent values
            message_id, action, payload = message[1], message[2], message[3]

            # Checking if the action sent is a valid OCPP action
            try:
                action = OCPPCommands[action]
            except:
                logger.critical(f"Charger '{self.charger_id}' sent a Call message with an invalid OCPP action of '{action}'")
                return

            # Performing the callback function for this action
            try:
                response = getattr(Call.Callbacks, action.name)(
                    message_id = message_id,
                    call_payload = payload
                )
                logger.info(f"For the message with the id '{message_id}' and action '{action.name}' created the response: {response}")
            except AttributeError:
                logger.warning(f"Charger '{self.charger_id}' sent an action of '{action.name}' which the server could not handle")
            except:
                logger.exception(f"Charger '{self.charger_id}' sent an action of '{action.name}' which the server could not handle")
            else:
                # Sending the created response back
                await self.channel_layer.group_send(
                    self.charger_group,
                    {
                        'type': 'send_ocpp_message',
                        'message': json.dumps(response)
                    }
                )

                # Saving the call recieved and the call result created
                logger.info(f"Creating the linkage for the message of the ID: {message_id} sent by charger '{self.charger_id}'")
                
                call_obj = ocpp_models.Call(
                    message_type_id = message_type_id.value,
                    message_id = message_id,
                    action = action.name,
                    payload = payload,

                    charger_id = self.charger_id,
                    sent_at = datetime.datetime.utcnow(),
                    direction = 'C2S',
                )

                call_result_obj = ocpp_models.CallResult(
                    message_type_id = response[0],
                    message_id = response[1],
                    payload = response[2],

                    charger_id = self.charger_id,
                    sent_at = datetime.datetime.utcnow(),
                    direction = 'S2C',
                )

                await self.save_and_link_call_and_result(call_obj, call_result_obj)

        elif message_type_id == OCPPMessageType.CALL_RESULT:
            logger.info(f"Charger '{self.charger_id}' sent a Call Result message")

            # Deserializing the call result message
            message_id, payload = message[1:]

            # All we do here is perform the linkage between the call and the call result.
            call_obj = await sync_to_async(ocpp_models.Call.objects.filter)(message_id = message_id)

            # If we were able to find a call object with the same message_id then
            # everything is okay
            if await sync_to_async(len)(call_obj) > 0:
                call_obj = call_obj[0]

                call_result_obj = ocpp_models.CallResult(
                    message_type_id = message_type_id.value,
                    message_id = message_id,
                    payload = payload,

                    charger_id = self.charger_id,
                    sent_at = datetime.datetime.utcnow(),
                    direction = 'C2S',

                    call_obj = call_obj
                )

                await self.save_and_link_call_and_result(call_obj, call_result_obj)

            # In this case we were either not able to find the message with the matching
            # id or we found multiple messages with a matching ID which is a problem
            else:
                logger.critical(f"Attempted to find a call message with the message id of '{message_id}' but was not able to find any. Number of search results {len(call_obj)}")

        elif message_type_id == OCPPMessageType.CALL_ERROR:
            logger.info(f"Charger '{self.charger_id}' sent a Call Error message")

    # Method used to send OCPP messages to the group
    async def send_ocpp_message(self, event):
        await self.send(text_data = event['message'])


class ExternalCommandsConsumer(AsyncWebsocketConsumer):
    '''
    The consumer concerned with the external commands of the charger

    ## Description
    This main purpose of this consumer is to accept external commands sent by
    any external entity. This consumer will then translate these commands into
    their appropriate OCPP commands and then send them to the charger. If a 
    response is expected then the websocket will respond back. 
    '''

    async def connect(self):
        # Getting the charger ID from the URL that the charger 
        # visited
        self.charger_id = self.scope['url_route']['kwargs']['charger_id']
        self.external_commands_group = f'externalCommands_{self.charger_id}'

        # Logging the visit
        logger.info(f"External Commands for charger with ID '{self.charger_id}' connected")

        # Making this charger join the room group
        await self.channel_layer.group_add(
            self.external_commands_group,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Logging the exit
        logger.info(f"External Commands for charger with ID '{self.charger_id}' disconnected")

        # Leave room group
        await self.channel_layer.group_discard(
            self.external_commands_group,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Deserializing the message sent.
        message = json.loads(text_data)
        logger.info(f"Recieved external command for the charger '{self.charger_id}' containing: {message}")