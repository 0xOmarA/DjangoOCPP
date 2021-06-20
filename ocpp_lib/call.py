# --------------------------------------------------- #
# This file contains a number of important classes    #
# for the OCPP library. The parent class is the Call  #
# class that has the 'CallHandler' and the            #
# 'Callbacks' classes. The 'CallHandler' class is a   #
# class which is used to issue Call commands to the   #
# charging point and it allows the programmer to      #
# await the response of the charging point. While the #
# callbacks class has the callback function which are #
# done when a CallResult of their respective type is  #
# received.                                           #
#                                                     #
# Author: Omar A. Sinoussy                            #
# Date: 12-Jun-2021                                   #
# --------------------------------------------------- #

import datetime, json, time, logging, asyncio, concurrent.futures
from ocpp_lib.utils import random_message_id
from os import stat
from typing import Union
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from api import models as ocpp_models
from channels.db import database_sync_to_async

from . import decorators, utils
from . import types as ocpp_types
from .types import (
    OcppType, 

    IdTagInfo,
    IdToken,
    ChargingProfile,
    
    Authorize_Conf, 
    BootNotification_Conf, 
    StatusNotification_Conf, 
    StartTransaction_Conf, 
    StopTransaction_Conf, 
    MeterValues_Conf,
    Heartbeat_Conf,
    FirmwareStatusNotification_Conf,
    DiagnosticsStatusNotification_Conf,
    DataTransfer_Conf,
)

from .enums import (
    AuthorizationStatus,
    DataTransferStatus,
    OCPPCommands,
    RegistrationStatus,
    OCPPMessageType
)

from .exceptions import (
    OCPPInvalidCommand,
    OCPPInvalidType
)

logger = logging.getLogger('ocpp')

class Call():
    # The ID used in the messages
    ID = OCPPMessageType.CALL

    class CallHandler():
        '''
        Used to make calls to a specific charger with an OCPP command

        ## Description
        The main purpose of this class is being used to make calls to certain 
        chargers connected to the central system. This class will also await the 
        charger's response if the correct arguments are given. As a summary, this
        class issues Call requests to the chargers.
        '''

        @staticmethod
        @database_sync_to_async
        def __save_call(message_type:OCPPMessageType, message_id:str, action:OCPPCommands, payload:dict, charger_id:str) -> ocpp_models.Call:
            '''
            Saves a call message to the Django database using the models

            ## Description
            This method takes in the arguments required for a call to be made and then
            saves this call to the databse by using the Django `Call` model in the api
            app. 

            ## Parameters
            - `message_type` (OCPPMessageType): The OCPP message type id. Since this is 
            a call then we are expecting the `message_type` to be 2.
            - `message_id` (str): The unique message id to use in saving the call object
            - `action` (OCPPCommands): The action in the OCPP message.
            - `payload` (dict): The payload in the OCPP message.
            - `charger_id` (str): A string of the `charger id` to issue the command to
            '''

            # Creating and saving and the call object
            call_object = ocpp_models.Call(
                message_type_id = message_type.value,
                message_id = message_id,
                action = action.value,
                payload = payload,

                charger_id = charger_id,
                sent_at = datetime.datetime.utcnow(),
                direction = 'S2C',
            )
            call_object.save()

            # Returning the call object
            return call_object

        @staticmethod
        async def __await_response(message_id:str, await_period:float, await_interval:float = 0.2) -> list:
            '''
            Awaits the client's response to the message with the same message_id

            ## Description
            This is a private method that takes in the `message_id` and the `await_period` and
            then based on these parameters it will await for the client response to the registered
            in the database. If the client did not respond during the `await_period` specified, then
            the function will return a None. 

            ## Parameters
            - `message_id` (str): A string of the message id. This should be the same as the message id 
            that the call request was sent with. This way, the call and call result can be matched to 
            each other.
            - `await_period` (float): The total period (in seconds) that the function is allowed to wait 
            before declaring the message as being lost or not arriving. Typically, if you set this for too
            long of a period you could have performance issues. But you should also understand that too
            short of a perido might not be enough for the response to be obtained by the server. Keep a 
            balance between these two.
            - `await_interval` (float): A float of how often (in seconds) should the function check the database
            for the arrival of the call result for this message. Has a default value of 0.2 seconds.

            ## Returns
            - `list`: A list which follows the OCPP standard for a call_result.
            '''

            # The total number of cycles which we will await
            await_cycles = int(await_period / await_interval)

            # Using a for loop to wait for this period
            for i in range(0, await_cycles, 1):
                try:
                    objects = await sync_to_async(ocpp_models.CallResult.objects.get)(message_id = message_id)
                    return objects.message_type_id, objects.message_id, objects.payload
                except:
                    pass

                await asyncio.sleep(await_interval)

            # If no object has been found then return None
            logger.warning(f"Sent a call message with the ID '{message_id}' but no call result was recieved back.")
            return None

        @staticmethod
        async def issue_command(charger_id:str, request:OcppType, shouldAwait:bool = True, await_period:int = 10, await_interval=0.2) -> Union[dict,None]:
            '''
            Issues call commands to the `charger_id` given.

            ## Description
            This method is used to issue commands to the charger. This command is the baseline
            command for sending other commands. The only purpose of other commands is to make 
            sure that the types match and are correct. So, this command should not be used on 
            its own outside the CallHandler class

            ## Parameters
            - `charger_id` (str): A string of the `charger id` to issue the command to
            - `request` (OcppType): The request which should be issued to the charger. 
            - `shouldAwait` (bool): A boolean of whether the function should await the response of
            the charger or should it only issue the request and leave. 
            - `await_period` (float): The total period (in seconds) that the function is allowed to wait 
            before declaring the message as being lost or not arriving. Typically, if you set this for too
            long of a period you could have performance issues. But you should also understand that too
            short of a perido might not be enough for the response to be obtained by the server. Keep a 
            balance between these two.
            - `await_interval` (float): A float of how often (in seconds) should the function check the database
            for the arrival of the call result for this message. Has a default value of 0.2 seconds.

            ## Returns
            - `dict` or `None`: A dictionary or None. If `shouldAwait` is false then it will always
            return `None`. But, if `shouldAwait` is True, then it will return a `dict` if it's able
            to match a call to a call_result. It will return a `None` if no match could be made in 
            the database
            '''
            
            # Checking the request class and subclass to make sure that they
            # match what is expected
            try:
                getattr(ocpp_types, request.__class__.split('.')[-1])
            except:
                raise OCPPInvalidType(f"An invalid request was sent. The request has a class of {request.__class__} but only requests from the ocpp_lib.types are accepted.")

            # Creating the request and getting the full OCPP message
            ocpp_message:list = [
                OCPPMessageType.CALL.value,
                utils.random_message_id(),
                str(type(request)).split('.')[-1].strip("'>").split('_')[0],
                request.serialize()
            ]

            # Getting the elements of the message
            message_type, message_id, action, payload = ocpp_message

            # Saving the call object to the database
            await Call.CallHandler.__save_call(
                message_type = OCPPMessageType(message_type),
                message_id = message_id,
                action = OCPPCommands[action],
                payload = payload,
                charger_id = charger_id
            )

            # Getting the django channels channel_layer and then sending it the OCPP message
            await get_channel_layer().group_send(
                f'ocpp_{charger_id}',
                {
                    'type': 'send_ocpp_message',
                    'message': json.dumps(ocpp_message)
                }
            )

            # If the function was asked to await for a response
            if shouldAwait:
                return await Call.CallHandler.__await_response(message_id = message_id, await_period = await_period, await_interval=await_interval)

            # Return the correct return type depending on whether the 
            # should return flag is true or false
            return None

    class Callbacks():
        '''
        The callback functions used when a call is recieved.

        ## Description
        This class is comprimised of callback functions which are used when a
        call is recieved. Since this means that the server has received a call 
        from the client, the callback functions here will respond with a message
        of the type CALL_RESULT
        '''

        @staticmethod
        @decorators.call_result_message_decorator
        def Authorize(message_id:str, call_payload:dict) -> Authorize_Conf:
            '''
            A callback function for the OCPP `Authorize` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `Authorize`. The result of this callback function is a return of a payload
            which will be created into a call_result object.

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return Authorize_Conf(
                idTagInfo = IdTagInfo(
                    status = AuthorizationStatus.Accepted,
                )
            )

        @staticmethod
        @decorators.call_result_message_decorator
        def BootNotification(message_id:str, call_payload:dict) -> BootNotification_Conf:
            '''
            A callback function for the OCPP `BootNotification` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `BootNotification`. The result of this callback function is a return of a 
            payload which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return BootNotification_Conf(
                currentTime = datetime.datetime.utcnow(),
                interval = 10,
                status = RegistrationStatus.Accepted
            )

        @staticmethod
        @decorators.call_result_message_decorator
        def StatusNotification(message_id:str, call_payload:dict) -> StatusNotification_Conf:
            '''
            A callback function for the OCPP `StatusNotification` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `StatusNotification`. The result of this callback function is a return of 
            a payload which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return StatusNotification_Conf()

        @staticmethod
        @decorators.call_result_message_decorator
        def StartTransaction(message_id:str, call_payload:dict) -> StartTransaction_Conf:
            '''
            A callback function for the OCPP ` StartTransaction` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `StartTransaction`. The result of this callback function is a return of 
            a payload which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return StartTransaction_Conf(
                idTagInfo = IdTagInfo(
                    status = AuthorizationStatus.Accepted,
                ),
                transactionId = 1
            )

        @staticmethod
        @decorators.call_result_message_decorator
        def StopTransaction(message_id:str, call_payload:dict) -> StopTransaction_Conf:
            '''
            A callback function for the OCPP ` StopTransaction` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `StopTransaction`. The result of this callback function is a return of 
            a payload which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return StopTransaction_Conf()

        @staticmethod
        @decorators.call_result_message_decorator
        def MeterValues(message_id:str, call_payload:dict) -> MeterValues_Conf:
            '''
            A callback function for the OCPP ` MeterValues` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `MeterValues`. The result of this callback function is a return of 
            a payload which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return MeterValues_Conf()

        @staticmethod
        @decorators.call_result_message_decorator
        def Heartbeat(message_id:str, call_payload:dict) -> Heartbeat_Conf:
            '''
            A callback function for the OCPP ` Heartbeat` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `Heartbeat`. The result of this callback function is a return of a payload 
            which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return Heartbeat_Conf(currentTime = datetime.datetime.utcnow())
        
        @staticmethod
        @decorators.call_result_message_decorator
        def FirmwareStatusNotification(message_id:str, call_payload:dict) -> FirmwareStatusNotification_Conf:
            '''
            A callback function for the OCPP ` FirmwareStatusNotification` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `FirmwareStatusNotification`. The result of this callback function is a return of a payload 
            which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return FirmwareStatusNotification_Conf()
        
        @staticmethod
        @decorators.call_result_message_decorator
        def DiagnosticsStatusNotification(message_id:str, call_payload:dict) -> DiagnosticsStatusNotification_Conf:
            '''
            A callback function for the OCPP ` DiagnosticsStatusNotification` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `DiagnosticsStatusNotification`. The result of this callback function is a return of a payload 
            which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return DiagnosticsStatusNotification_Conf()

        @staticmethod
        @decorators.call_result_message_decorator
        def DataTransfer(message_id:str, call_payload:dict) -> DataTransfer_Conf:
            '''
            A callback function for the OCPP ` DataTransfer` action

            ## Description 
            This callback function is performed when a call request comes with an action
            of `DataTransfer`. The result of this callback function is a return of a payload 
            which will be created into a call_result object

            ## Parameters
            - `message_id` (str): A unique message ID which will be used by the decorator to 
            create the Call Result using that message ID.
            - `call_payload` (dict): A dictionary of the payload sent in the CALL message.
            '''

            # Returning the response back
            return DataTransfer_Conf(
                status = DataTransferStatus.Accepted,
            )