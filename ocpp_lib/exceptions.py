# ------------------------------------------------ #
# Contains a number of exceptions used in the OCPP #
# library                                          #
#                                                  #
# Author: Omar A. Sinoussy                         #
# Date: 12-Jun-2021                                #
# ------------------------------------------------ #

class OCPPInvalidCommand(Exception):
    '''A base class exception used when an invalid ocpp command is used.'''
    pass

class OCPPInvalidType(Exception):
    '''A base class for the invalid OCPP type exception'''
    pass