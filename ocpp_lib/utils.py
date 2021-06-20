# ------------------------------------------------- #
# Contains a number of useful functions and methods #
# used in the OCPP library                          #
#                                                   #
# Author: Omar A. Sinoussy                          #
# Date: 12-Jun-2021                                 #
# ------------------------------------------------- #

import random, string

def random_message_id(length = 16) -> str:
    '''
    Creates a random message ID and returns it.

    A method used to create a random message ID and then return it back to the 
    user. This method has a default length of 16. Note: this method does not 
    check for conflicts in the message ID. This must be done separately

    @param length The length of the random id to create.
    @return A string of the random message id
    '''
    return "".join([random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length)])