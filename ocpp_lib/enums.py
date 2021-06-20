# -------------------------------------------------- #
# This file contains the enums used in the OCPP 1.6  #
# as detailed by their documentation. In most cases, #
# the enum maps to a string that has the same value  #
# as the enum for serialization purposes             #
#                                                    #
# Author: Omar A. Sinoussy                           #
# Date: 12-Jun-2021                                  #
# -------------------------------------------------- #

from enum import Enum, auto

class OCPPMessageType(Enum):
    '''
    The type of the OCPP message being sent.

    ## Description 
    In the OCPP standard there are three types of messages that can be sent.
    A `call`, `call_result`, and a `call_error` which are defined by certain the numbers
    2, 3, and 4 respectivly 
    '''
    
    CALL        = 2
    CALL_RESULT = 3
    CALL_ERROR  = 4

class OCPPCommands(Enum):
    '''
    All of the OCPP commands in OCPP 1.6

    ## Description 
    This enum has a list of all of the commands in the OCPP standard as of version 1.6. Any
    other command that is outside of this is considered as not belonging to OCPP.
    '''
    
    Authorize                       = auto()
    BootNotification                = auto()
    CancelReservation               = auto()
    ChangeAvailability              = auto()
    ChangeConfiguration             = auto()
    ClearCache                      = auto()
    ClearChargingProfile            = auto()
    DataTransfer                    = auto()
    DiagnosticsStatusNotification   = auto()
    FirmwareStatusNotification      = auto()
    GetCompositeSchedule            = auto()
    GetConfiguration                = auto()
    GetDiagnostics                  = auto()
    GetLocalListVersion             = auto()
    Heartbeat                       = auto()
    MeterValues                     = auto()
    RemoteStartTransaction          = auto()
    RemoteStopTransaction           = auto()
    ReserveNow                      = auto()
    SendLocalList                   = auto()
    SetChargingProfile              = auto()
    StartTransaction                = auto()
    StatusNotification              = auto()
    StopTransaction                 = auto()
    TriggerMessage                  = auto()
    UnlockConnector                 = auto()
    UpdateFirmware                  = auto()

class AuthorizationStatus(Enum):
    '''
    An enum used for the status in `Authorization` requests
    '''
    
    Accepted        = "Accepted"        # Identifier is allowed for charging.
    Blocked         = "Blocked"         # Identifier has been blocked. Not allowed for charging.
    Expired         = "Expired"         # Identifier has expired. Not allowed for charging.
    Invalid         = "Invalid"         # Identifier is unknown. Not allowed for charging.
    ConcurrentTx    = "ConcurrentTx"    # Identifier is already involved in another transaction and multiple transactions are not allowed. (Only relevant for a StartTransaction.req.)

class RegistrationStatus(Enum):
    '''
    An enum used for the status in `BootNotification` requests
    '''
    
    Accepted        = "Accepted"    # Charge point is accepted by Central System.
    Pending         = "Pending"     # Central System is not yet ready to accept the Charge Point. Central System may send messages to retrieve information or prepare the Charge Point.
    Rejected        = "Rejected"    # Charge point is not accepted by Central System. This may happen when the Charge Point id is not known by Central System.

class RemoteStartStopStatus(Enum):
    '''
    An enum used for the status in `RemoteStartTransaction` and 
    `RemoteStopTransaction` requests
    '''
    
    Accepted        = "Accepted"    # Command will be executed.
    Rejected        = "Rejected"    # Command will not be executed.

class ChargingProfilePurposeType(Enum):
    '''
    An enum used for the charging purpose in the `SetChargingProfile`
    '''
    
    ChargePointMaxProfile   = "ChargePointMaxProfile"   # Configuration for the maximum power or current available for an entire Charge Point. SetChargingProfile.req message.
    TxDefaultProfile        = "TxDefaultProfile"        # Default profile to be used for new transactions.
    TxProfile               = "TxProfile"               # Profile with constraints to be imposed by the Charge Point on the current transaction. A profile with this purpose SHALL cease to be valid when the transaction terminates.

class ChargingRateUnitType(Enum):
    '''
    An enum used for the charging unit type in the `SetChargingProfile`
    '''

    W   = "W"   # Watts (power).
    A   = "A"   # Amperes (current).

class ChargingProfileKindType(Enum):
    '''
    An enum used for the charging profile type in the `SetChargingProfile`
    '''

    Absolute    = "Absolute"    # Schedule periods are relative to a fixed point in time defined in the schedule.
    Recurring   = "Recurring"   # The schedule restarts periodically at the first schedule period.
    Relative    = "Relative"    # Schedule periods are relative to a situation- specific start point (such as the start of a session) that is determined by the charge point.

class RecurrencyKindType(Enum):
    '''
    An enum used for the recurrency of the charging profile
    '''

    Daily       = "Daily"       # The schedule restarts at the beginning of the next day.
    Weekly      = "Weekly"      # The schedule restarts at the beginning of the next week (defined as Monday morning)

class AvailabilityType(Enum):
    '''
    An enum used for the type of the availability of the chargers
    '''

    Inoperative = "Inoperative" # Charge point is not available for charging.
    Operative   = "Operative"   # Charge point is available for charging.

class MessageTrigger(Enum):
    '''
    An enum used to trigger messages from the chargers.
    '''

    BootNotification                = "BootNotification"                # To trigger a BootNotification request
    DiagnosticsStatusNotification   = "DiagnosticsStatusNotification"   # To trigger a DiagnosticsStatusNotification request
    FirmwareStatusNotification      = "FirmwareStatusNotification"      # To trigger a FirmwareStatusNotification request
    Heartbeat                       = "Heartbeat"                       # To trigger a Heartbeat request
    MeterValues                     = "MeterValues"                     # To trigger a MeterValues request
    StatusNotification              = "StatusNotification"              # To trigger a StatusNotification request

class ResetType(Enum): 
    '''
    An enum type describing the type of reset that should be made
    '''

    Hard    = "Hard"    # Full reboot of Charge Point software.
    Soft    = "Soft"    # Return to initial status, gracefully terminating any transactions in progress.

class UpdateType(Enum):
    '''
    An enum used for the type of the update sent in the `SetLocalList` requests
    '''

    Differential    = "Differential"    # Indicates that the current Local Authorization List must be updated with the values in this message.
    Full            = "Full"            # Indicates that the current Local Authorization List must be replaced by the values in this message.

class DataTransferStatus(Enum):
    '''
    An enum used to describe the status of data transfer.
    '''

    Accepted            = "Accepted"            # Message has been accepted and the contained request is accepted.
    Rejected            = "Rejected"            # Message has been accepted but the contained request is rejected.
    UnknownMessageId    = "UnknownMessageId"    # Message could not be interpreted due to unknown messageId string.
    UnknownVendorId     = "UnknownVendorId"     # Message could not be interpreted due to unknown vendorId string.