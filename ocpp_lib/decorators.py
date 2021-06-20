# --------------------------------------------------- #
# This file contains a number of decorators which are #
# used to create the ocpp messages that the function  #
# return. The main use of these decorators is taking  #
# the functions, adding to them the message_type,     #
# message_id, action, and their payload. Reduces the  #
# repetition in the code.                             #
#                                                     #
# Author: Omar A. Sinoussy                            #
# Date: 12-Jun-2021                                   #
# --------------------------------------------------- #

from . import enums, utils, exceptions

def call_message_decorator(function):
    '''
    A decorator used for OCPP CALL messages

    ## Description 
    This decortator is used to take a standard function that returns a dictionary 
    and use its return to create a valid OCPP CALL message. The format that this 
    decorator uses is that which is provided by the OCPP team in their documentation
    for the calls. So, the format is `[ message_type_id, message_id, action, payload ]`.

    ## Parameters
    - `function` (function): The function that returns the payload

    ## Returns
    - `function`: A new function with the modifications needed

    ## Raises
    - `ValueError`: Occurs when the function provided does not return a dictionary
    - `OCPPInvalidCommand`: Occurs when an invalid OCPP command is issued.
    '''
    def inner(*args, **kwargs):
        # Performing the function and getting the payload
        # provided by it. Then we serialize it. This is a 
        # feature provided by the `OcppType` class
        try:
            payload = function(*args, **kwargs).serialize()
        except:
            payload = function(*args, **kwargs)

        # Ensuring that the function returned a valid payload
        # that is a dict
        if type(payload) != dict:
            raise ValueError(f"Function '{function.__name__}' must return a dict.")

        # Checking if the function name is of a valid OCPP command.
        # if its not of a valid OCPP command then throw an Exception
        try:
            if function.__name__ != "serialize":
                enums.OCPPCommands[function.__name__]
        except:
            raise exceptions.OCPPInvalidCommand(f"The command {function.__name__} is not a valid OCPP command")

        return [
            # A Call message type
            enums.OCPPMessageType.CALL.value,

            # Creating a Random Message ID and assigning
            # it to the message.
            utils.random_message_id(),

            # The name of the function is the action name
            # So, the function name must be a valid OCPP
            # action
            function.__name__,
            
            # Adding the payload to the return
            payload
        ]

    return inner

def call_result_message_decorator(function):
    '''
    A decorator used for OCPP CALL_RESULT messages

    ## Description 
    This decortator is used to take a standard function that returns a dictionary 
    and use its return to create a valid OCPP CALL_RESULT message. The format that this 
    decorator uses is that which is provided by the OCPP team in their documentation
    for the calls. So, the format is `[ message_type_id, message_id, payload ]`.

    ## Parameters
    - `function` (function): The function that returns the payload

    ## Returns
    - `function`: A new function with the modifications needed

    ## Raises
    - `ValueError`: Occurs when the function provided does not return a dictionary
    - `KeyError`: If no `message_id` is provided in the parent function as a keyword
    argument
    '''
    def inner(*args, **kwargs):
        # Performing the function and getting the payload
        # provided by it
        try:
            payload = function(*args, **kwargs).serialize()
        except:
            payload = function(*args, **kwargs)

        # Ensuring that the function returned a valid payload
        # that is a dict
        if type(payload) != dict:
            raise ValueError(f"Function '{function.__name__}' must return a dict.")

        # Checking if a message_id argument was passed in the kwargs. Throwing an
        # exception if it was not
        if 'message_id' not in kwargs.keys():
            raise KeyError("No message_id was passed in the keyword arguments. Did you pass a message_id? Are you sure that the message_id is passed as a named argument?")

        return [
            # A Call Result message type
            enums.OCPPMessageType.CALL_RESULT.value,

            # Getting the mssage id which was passed to the
            # original function as a keyword argyment
            kwargs.get('message_id'),
            
            # Adding the payload to the return
            payload
        ]

    return inner