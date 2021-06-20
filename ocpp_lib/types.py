# ------------------------------------------------- #
# A very important file that contains all of the    #
# types used in the OCPP 1.6 standard. The OcppType #
# class is the parent class which all other classes #
# inherit from. This class allows the objects to be #
# serializable. Other types inherit from the OCPP   #
# type.                                             #
#                                                   #
# Author: Omar A. Sinoussy                          #
# Date: 12-Jun-2021                                 #
# ------------------------------------------------- #

from typing import Any, Union, List
from .enums import AuthorizationStatus, AvailabilityType, ChargingProfileKindType, ChargingProfilePurposeType, ChargingRateUnitType, DataTransferStatus, MessageTrigger, RegistrationStatus, RemoteStartStopStatus, RecurrencyKindType, UpdateType
import datetime, json, enum

# If the doc strings are too much, use the 
# regex '''[\w\W]*?''' to remove it :)

class OcppType():
    '''
    A parent class used to define an OCPP Type. 

    ## Description
    An OCPP type is any type that is not built into the Python programming language
    by default. In most cases these types are JSON serializeable objects
    '''

    def __init__(self, *args:list, **kwargs:dict):
        '''
        The main constructor to the OcppType class

        ## Description
        This constructor takes in a data variable and assigns it to the `self.__data`.
        This variable is what we use for the serialization of the data

        ## Parameters
        - `data` (dict): A dictionary of the data which we will serialize. This data is often
        the kwargs argument. In this case, all `None` values will be removed from it
        '''
        self.__data = {key:value for key,value in kwargs.items() if value != None}

    def serialize(self) -> dict:
        '''
        A method used to serialize the OCPP object.

        ## Description
        This method performs serialization on the `data` argument passed to the class 
        constructor. 

        ## Returns
        - `dict`: A dict of the serialized data
        '''
        def single_value_serialize(value:Any) -> Union[str,dict,int,float]:
            '''
            Serializes a single value to its correct object type

            ## Description
            A method used to convert an object of any type to its correct type. This method
            is an internal method which is only accessible within the `serialize` function.

            ## Retuens
            - `Any`: An object of any type
            '''
            
            # If the value is an Enum
            if isinstance(value, enum.Enum):
                return value.value

            # If the value if a date time object
            elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                return value.isoformat()

            # If the object is a subclass of OcppType
            elif issubclass(value.__class__, OcppType):
                return value.serialize()

            # If the object is already of an acceptable data type
            elif isinstance(value, int) or isinstance(value, float) or isinstance(value, bool) or isinstance(value, str):
                return value 
            
            # If we find that the item is a list, then we serialize each of them
            elif isinstance(value, list):
                value = [one.serialize() if issubclass(value.__class__, OcppType) else one for one in list]

            # If none of the above is the case then we dont know how to serialize this
            else:
                raise ValueError(f"An object of the type `{type(value)}` and the class `{value.__class__}` does not have any known serialization methods")

        return {key:single_value_serialize(value) for key,value in self.__data.items()}

    def __str__(self) -> str:
        '''
        Converts the data to a JSON String

        ## Description
        A method used to convert the data passed to the constructor to a JSON string

        ## Returns
        - `str`: A string of the serialized data
        '''
        return json.dumps(self.serialize())

    def __repr__(self) -> str:
        '''
        Converts the data to a JSON String

        ## Description
        A method used to convert the data passed to the constructor to a JSON string

        ## Returns
        - `str`: A string of the serialized data
        '''
        return str(self)

# ------------------------------------------------------
# Basic data types which other types will be built upon
# ------------------------------------------------------

class IdToken(OcppType):
    '''
    A class which describes the `IdToken` datatype in the OCPP documentation
    '''

    def __init__(self, IdToken:str):
        '''
        The main constructor to the `IdToken` class

        ## Description
        Contains the identifier to use for authorization. It is a case insensitive string. 
        In future releases this may become a complex type to support multiple forms of 
        identifiers.

        ## Parameters
        - `IdToken` (str): Required. Required. IdToken is case insensitive.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class IdTagInfo(OcppType):
    '''
    A class which describes the `IdTagInfo` datatype in the OCPP documentation
    '''
   
    def __init__(self, status:AuthorizationStatus, parentIdTag:IdToken = None, expiryDate:datetime.datetime = None):
        '''
        The main constructor to the `IdTagInfo` class

        ## Description
        Contains status information about an identifier. It is returned in Authorize, 
        Start Transaction and Stop Transaction responses. If expiryDate is not given, 
        the status has no end date.

        ## Parameters
        - `status` (AuthorizationStatus): Required. This contains whether the idTag 
        has been accepted or not by the Central System.
        - `parentIdTag` (IdToken): Optional. This contains the parent-identifier.
        - `expiryDate` (datetime.datetime): Optional. This contains the date at which 
        idTag should be removed from the Authorization Cache.
        '''
        
        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ChargingSchedulePeriod(OcppType):
    '''
    A class which describes the `ChargingSchedulePeriod` datatype in the OCPP documentation
    '''

    def __init__(self, startPeriod:int, limit:float, numberPhases:int = None):
        '''
        The main constructor to the `ChargingSchedule` class

        ## Description
        A `ChargingSchedulePeriod` has the current or the power which the car is expected
        to be charged at and is the final layer in the complex Charging profile tree

        ## Parameters
        - `startPeriod` (int): Required. Start of the period, in seconds from the start of 
        schedule. The value of StartPeriod also defines the stop time of the previous period.
        has been accepted or not by the Central System.
        - `limit` (float): Required. Power limit during the schedule period, expressed in Amperes. 
        Accepts at most one digit fraction (e.g. 8.1).
        - `numberPhases` (int): Optional. The number of phases that can be used for charging.
        If a number of phases is needed, numberPhases=3 will be assumed unless another number is given.
        '''
        
        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ChargingSchedule(OcppType):
    '''
    A class which describes the `ChargingSchedule` datatype in the OCPP documentation
    '''
   
    def __init__(self, chargingRateUnit:ChargingRateUnitType, chargingSchedulePeriod:List[ChargingSchedulePeriod], duration:int = None, startSchedule:datetime.datetime = None, minChargingRate:float = None):
        '''
        The main constructor to the `ChargingSchedule` class

        ## Description
        A ChargingSchedule describes in detail what the car needs to have as its max
        current.

        ## Parameters
        - `chargingRateUnit` (ChargingRateUnitType): Required. The unit of measure Limit 
        is expressed in.
        - `chargingSchedulePeriod` (List[ChargingSchedulePeriod]): Required. List of 
        `ChargingSchedulePeriod` elements defining maximum power or current usage over time.
        - `duration` (int): Optional. Duration of the charging schedule in seconds. If the 
        duration is left empty, the last period will continue indefinitely or until end of 
        the transaction in case startSchedule is absent.
        - `startSchedule` (datetime.datetime): Optional. Starting point of an absolute schedule. 
        If absent the schedule will be relative to start of charging.
        - `minChargingRate` (float): Optional. Minimum charging rate supported by the 
        electric vehicle. The unit of measure is defined by the chargingRateUnit. This 
        parameter is intended to be used by a local smart charging algorithm to optimize 
        the power allocation for in the case a charging process is inefficient at lower 
        charging rates. Accepts at most one digit fraction (e.g. 8.1)
        '''
        
        # Checking if the chargingSchedulePeriod is a list or not. 
        # Casting it to a list if its not 
        chargingSchedulePeriod = chargingSchedulePeriod if isinstance(chargingSchedulePeriod, list) else [chargingSchedulePeriod]

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ChargingProfile(OcppType):
    '''
    A class which describes the `ChargingProfile` datatype in the OCPP documentation
    '''
   
    def __init__(self, chargingProfileId:int, stackLevel:int, chargingProfilePurpose:ChargingProfilePurposeType, chargingProfileKind:ChargingProfileKindType, chargingSchedule:ChargingSchedule, transactionId:int = None, recurrencyKind:RecurrencyKindType = None, validFrom:datetime.datetime = None, validTo:datetime.datetime = None):
        '''
        The main constructor to the `ChargingProfile` class

        ## Description
        A ChargingProfile consists of a ChargingSchedule, describing the amount of power 
        or current that can be delivered per time interval.

        ## Parameters
        - `chargingProfileId` (int): Required. Unique identifier for this profile.
        - `stackLevel` (int): Required. Value determining level in hierarchy stack of profiles. 
        Higher values have precedence over lower values. Lowest level is 0.
        - `chargingProfilePurpose` (ChargingProfilePurposeType): Required. Defines the purpose 
        of the schedule transferred by this message.
        - `chargingProfileKind` (ChargingProfileKindType): Required. Indicates the kind of 
        schedule.
        - `chargingSchedule` (ChargingSchedule): Required. Contains limits for the available power 
        or current over time.
        - `transactionId` (int): Optional. Only valid if ChargingProfilePurpose is set to TxProfile, 
        the transactionId MAY be used to match the profile to a specific transaction.
        - `recurrencyKind` (RecurrencyKindType): Optional. Indicates the start point of a recurrence.
        - `validFrom` (datetime.datetime): Optional. Point in time at which the profile starts to be 
        valid. If absent, the profile is valid as soon as it is received by the Charge Point. Not to
        be used when ChargingProfilePurpose is TxProfile.
        - `validTo` (datetime.datetime): Optional. Point in time at which the profile stops to be valid. 
        If absent, the profile is valid until it is replaced by another profile. Not to be used when 
        `ChargingProfilePurpose` is TxProfile.
        '''
        
        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class AuthorizationData(OcppType):
    '''
    A class which describes the `AuthorizationData` datatype in the OCPP documentation
    '''
   
    def __init__(self, idTag:IdToken, idTagInfo:IdTagInfo = None):
        '''
        The main constructor to the `AuthorizationData` class

        ## Description
        Elements that constitute an entry of a Local Authorization List update.

        ## Parameters
        - `idTag` (IdToken): Required. The identifier to which this authorization applies.
        - `idTagInfo` (IdTagInfo): Optional. (Required when `UpdateType` is Full) This contains information 
        about authorization status, expiry and parent id. For a Differential update the following applies: 
        If this element is present, then this entry SHALL be added or updated in the Local Authorization List. 
        If this element is absent, than the entry for this idtag in the Local Authorization List SHALL be deleted.
        '''
        
        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

# ------------------------------------------------------
# More complex return types which will be used as the 
# return types of the CALL and CALL_RESULT
# ------------------------------------------------------

class Authorize_Conf(OcppType):
    '''
    A class which describes the `Authorize.conf` datatype in the OCPP documentation
    '''

    def __init__(self, idTagInfo:IdTagInfo):
        '''
        The main constructor to the `Authorize_Conf` class

        ## Description
        This contains the field definition of the Authorize.conf PDU sent by the Central
        System to the Charge Point in response to a Authorize.req PDU. 

        ## Parameters
        - `idTagInfo` (IdTagInfo): Required. This contains information about authorization 
        status, expiry and parent id.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class BootNotification_Conf(OcppType):
    '''
    A class which describes the `BootNotification.conf` datatype in the OCPP documentation
    '''

    def __init__(self, currentTime:datetime.datetime, interval:int, status:RegistrationStatus):
        '''
        The main constructor to the `BootNotification_conf` class

        ## Description
        This contains the field definition of the BootNotification.conf PDU sent by the Central 
        System to the Charge Point in response to a BootNotification.req PDU.

        ## Parameters
        - `currentTime` (datetime.datetime): Required. This contains the Central System’s current 
        time.
        - `interval` (int): Required. When RegistrationStatus is Accepted, this contains the heartbeat 
        interval in seconds. If the Central System returns something other than Accepted, the value of 
        the interval field indicates the minimum wait time before sending a next BootNotification 
        request.
        - `status` (RegistrationStatus): Required. This contains whether the Charge Point has been 
        registered within the System Central.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class StatusNotification_Conf(OcppType):
    '''
    A class which describes the `StatusNotification.conf` datatype in the OCPP documentation
    '''

    def __init__(self):
        '''
        The main constructor to the `StatusNotification_Conf` class

        ## Description
        This contains the field definition of the StatusNotification.conf PDU sent by the Central System 
        to the Charge Point in response to an StatusNotification.req PDU
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class StartTransaction_Conf(OcppType):
    '''
    A class which describes the `StartTransaction.conf` datatype in the OCPP documentation
    '''

    def __init__(self, idTagInfo:IdTagInfo, transactionId:int):
        '''
        The main constructor to the `StartTransaction_Conf` class

        ## Description
        This contains the field definition of the StartTransaction.conf PDU sent by the Central System 
        to the Charge Point in response to an StartTransaction.req PDU
        
        ## Parameters
        - `idTagInfo` (IdTagInfo): Required. This contains information about authorization 
        status, expiry and parent id.
        - `transactionId` (int): Required. This contains the transaction id supplied by the 
        Central System.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class StopTransaction_Conf(OcppType):
    '''
    A class which describes the `StopTransaction.conf` datatype in the OCPP documentation
    '''

    def __init__(self, idTagInfo:IdTagInfo = None):
        '''
        The main constructor to the `StopTransaction_Conf` class

        ## Description
        This contains the field definition of the StopTransaction.conf PDU sent by the Central System 
        to the Charge Point in response to an StopTransaction.req PDU
        
        ## Parameters
        - `idTagInfo` (IdTagInfo): Optional. This contains information about authorization 
        status, expiry and parent id.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class MeterValues_Conf(OcppType):
    '''
    A class which describes the `MeterValues.conf` datatype in the OCPP documentation
    '''

    def __init__(self):
        '''
        The main constructor to the `MeterValues_Conf` class

        ## Description
        This contains the field definition of the MeterValues.conf PDU sent by the Central System 
        to the Charge Point in response to an MeterValues.req PDU
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class Heartbeat_Conf(OcppType):
    '''
    A class which describes the `Heartbeat.conf` datatype in the OCPP documentation
    '''

    def __init__(self, currentTime:datetime.datetime):
        '''
        The main constructor to the `Heartbeat_Conf` class

        ## Description
        This contains the field definition of the Heartbeat.conf PDU sent by the Central System 
        to the Charge Point in response to an Heartbeat.req PDU

        ## Parameters
        - `currentTime` (datetime.datetime): Required. This contains the current time of the Central
        System.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class DataTransfer_Conf(OcppType):
    '''
    A class which describes the `DataTransfer.conf` datatype in the OCPP documentation
    '''

    def __init__(self, status:DataTransferStatus, data:str = None):
        '''
        The main constructor to the `DataTransfer_Conf` class

        ## Description
        This contains the field definition of the DataTransfer.conf PDU sent by the Central System 
        to the Charge Point in response to an DataTransfer.req PDU

        ## Parameters
        - `status` (DataTransferStatus): Required. This indicates the success or failure of the data
        transfer.
        - `data` (str): Optional. Data in response to request.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class DiagnosticsStatusNotification_Conf(OcppType):
    '''
    A class which describes the `DiagnosticsStatusNotification.conf` datatype in the OCPP documentation
    '''

    def __init__(self):
        '''
        The main constructor to the `DiagnosticsStatusNotification_Conf` class

        ## Description
        This contains the field definition of the DiagnosticsStatusNotification.conf PDU sent by the
        Central System to the Charge Point in response to an DiagnosticsStatusNotification.req PDU
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class  FirmwareStatusNotification_Conf(OcppType):
    '''
    A class which describes the ` FirmwareStatusNotification.conf` datatype in the OCPP documentation
    '''

    def __init__(self):
        '''
        The main constructor to the ` FirmwareStatusNotification_Conf` class

        ## Description
        This contains the field definition of the  FirmwareStatusNotification.conf PDU sent by the
        Central System to the Charge Point in response to an  FirmwareStatusNotification.req PDU
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class RemoteStartTransaction_Req(OcppType):
    '''
    A class which describes the `RemoteStartTransaction.Req` datatype in the OCPP documentation
    '''

    def __init__(self, idTag:IdToken, chargingProfile:ChargingProfile = None, connectorId:int = None):
        '''
        The main constructor to the `RemoteStartTransaction_Req` class

        ## Description
        This contains the field definition of the RemoteStartTransaction.Req PDU sent by the Central 
        System to the Charge Point in response to an RemoteStartTransaction.Req PDU
        
        ## Parameters
        - `idTag` (IdToken): Required. The identifier that Charge Point must use to start a transaction.
        - `chargingProfile` (ChargingProfile): Optional. Charging Profile to be used by the Charge Point 
        for the requested transaction. ChargingProfilePurpose MUST be set to TxProfile.
        - `connectorId` (int): Optional. Number of the connector on which to start the transaction. 
        connectorId SHALL be > 0
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class RemoteStopTransaction_Req(OcppType):
    '''
    A class which describes the `RemoteStopTransaction.Req` datatype in the OCPP documentation
    '''

    def __init__(self, transactionId:int):
        '''
        The main constructor to the `RemoteStopTransaction_Req` class

        ## Description
        This contains the field definition of the RemoteStopTransaction.Req PDU sent by the Central 
        System to the Charge Point in response to an RemoteStopTransaction.Req PDU
        
        ## Parameters
        - `transactionId` (int): Required. The identifier of the transaction which Charge Point is 
        requested to stop.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class GetLocalListVersion_Req(OcppType):
    '''
    A class which describes the `GetLocalListVersion.Req` datatype in the OCPP documentation
    '''

    def __init__(self, transactionId:int):
        '''
        The main constructor to the `GetLocalListVersion_req` class

        ## Description
        This contains the field definition of the GetLocalListVersion.req PDU sent by the Central
        System to the Charge Point.

        ## Parameters
        - `transactionId` (int): Required. This contains the current version number of the local 
        authorization list in the Charge Point.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ReserveNow_Req(OcppType):
    '''
    A class which describes the `ReserveNow.Req` datatype in the OCPP documentation
    '''

    def __init__(self, connectorId:int, expiryDate:datetime.datetime, idTag:IdToken, reservationId:int, parentIdTag:IdToken = None):
        '''
        The main constructor to the `ReserveNow_Req` class

        ## Description
        This contains the field definition of the ReserveNow.Req PDU sent by the Central System
        to the Charge Point.

        ## Parameters
        - `connectorId` (int): Required. This contains the id of the connector to be reserved. A
        value of 0 means that the reservation is not for a specific connector.
        - `expiryDate` (datetime.datetime): Required. This contains the date and time when the 
        reservation ends.
        - `idTag` (IdToken): Required. The identifier for which the Charge Point has to reserve 
        a connector.
        - `parentIdTag` (IdToken): Optional. The parent idTag.
        - `reservationId` (int): Required. Unique id for this reservation.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class CancelReservation_Req(OcppType):
    '''
    A class which describes the `CancelReservation.Req` datatype in the OCPP documentation
    '''

    def __init__(self, reservationId:int):
        '''
        The main constructor to the `CancelReservation_Req` class

        ## Description
        This contains the field definition of the CancelReservation.Req PDU sent by the Central System
        to the Charge Point.

        ## Parameters
        - `reservationId` (int): Required. Unique id for this reservation.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ChangeAvailability_Req(OcppType):
    '''
    A class which describes the `ChangeAvailability.Req` datatype in the OCPP documentation
    '''

    def __init__(self, connectorId:int, type:AvailabilityType):
        '''
        The main constructor to the `ChangeAvailability_Req` class

        ## Description
        This contains the field definition of the ChangeAvailability.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `connectorId` (int): Required. The id of the connector for which availability needs to 
        change. Id '0' (zero) is used if the availability of the Charge Point and all its 
        connectors needs to change.
        - `type` (AvailabilityType): Required. This contains the type of availability change that 
        the Charge Point should perform.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ChangeConfiguration_Req(OcppType):
    '''
    A class which describes the `ChangeConfiguration.Req` datatype in the OCPP documentation
    '''

    def __init__(self, key:str, value:str):
        '''
        The main constructor to the `ChangeConfiguration_Req` class

        ## Description
        This contains the field definition of the ChangeConfiguration.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `key` (str): Required. The name of the configuration setting to change. See for standard 
        configuration key names and associated values
        - `value` (str): Required. The new value as string for the setting. See for standard 
        configuration key names and associated values
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ClearChargingProfile_Req(OcppType):
    '''
    A class which describes the `ClearChargingProfile.Req` datatype in the OCPP documentation
    '''

    def __init__(self, id:int=None, connectorId:int=None, chargingProfilePurpose:ChargingProfilePurposeType = None, stackLevel:int = None):
        '''
        The main constructor to the `ClearChargingProfile_Req` class

        ## Description
        This contains the field definition of the ClearChargingProfile.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `id` (int): Optional. The ID of the charging profile to clear.
        - `connectorId` (int): Optional. Specifies the ID of the connector for which to clear charging 
        profiles. A connectorId of zero (0) specifies the charging profile for the overall Charge Point. 
        Absence of this parameter means the clearing applies to all charging profiles that match the 
        other criteria in the request.
        - `chargingProfilePurpose` (ChargingProfilePurposeType): Optional. Specifies to purpose of the
        charging profiles that will be cleared, if they meet the other criteria in the request.
        - `stackLevel` (int): Optional. specifies the stackLevel for which charging profiles will be 
        cleared, if they meet the other criteria in the request
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class ClearCache_Req(OcppType):
    '''
    A class which describes the `ClearCache.Req` datatype in the OCPP documentation
    '''

    def __init__(self):
        '''
        The main constructor to the `ClearCache_Req` class

        ## Description
        This contains the field definition of the ClearCache.Req PDU sent by the Central 
        System to the Charge Point.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class DataTransfer_Req(OcppType):
    '''
    A class which describes the `DataTransfer.Req` datatype in the OCPP documentation
    '''

    def __init__(self, vendorId:str, messageId:str, data:str):
        '''
        The main constructor to the `DataTransfer_Req` class

        ## Description
        This contains the field definition of the DataTransfer.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `vendorId` (str): Required. This identifies the Vendor specific implementation.
        - `messageId` (str): Optional. Additional identification field.
        - `data` (str): Optional. Data without specified length or format.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class SetChargingProfile_Req(OcppType):
    '''
    A class which describes the `SetChargingProfile.Req` datatype in the OCPP documentation
    '''

    def __init__(self, connectorId:int, csChargingProfiles:ChargingProfile):
        '''
        The main constructor to the `SetChargingProfile_Req` class

        ## Description
        This contains the field definition of the SetChargingProfile.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `connectorId` (int): Required. The connector to which the charging profile applies. 
        If connectorId = 0, the message contains an overall limit for the Charge Point.
        - `csChargingProfiles` (ChargingProfile): Required. The charging profile to be set at
        the Charge Point.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class TriggerMessage_Req(OcppType):
    '''
    A class which describes the `TriggerMessage.Req` datatype in the OCPP documentation
    '''

    def __init__(self, requestedMessage:MessageTrigger, connectorId:int):
        '''
        The main constructor to the `TriggerMessage_Req` class

        ## Description
        This contains the field definition of the TriggerMessage.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `requestedMessage` (MessageTrigger): Required. The type of the message to trigger the 
        charger to send. 
        - `connectorId` (int): Optional. Only filled in when request applies to a specific 
        connector.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class UpdateFirmware_Req(OcppType):
    '''
    A class which describes the `UpdateFirmware.Req` datatype in the OCPP documentation
    '''

    def __init__(self, location:str, retrieveDate:datetime.datetime, retries:int = None, retryInterval:int = None):
        '''
        The main constructor to the `UpdateFirmware_Req` class

        ## Description
        This contains the field definition of the UpdateFirmware.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `location` (str): Required. This contains a string containing a URI pointing to a 
        location from which to retrieve the firmware.
        - `retrieveDate` (datetime.datetime): Required. This contains the date and time after 
        which the Charge Point must retrieve the (new) firmware.
        - `retries` (int): Optional. This specifies how many times Charge Point must try to 
        download the firmware before giving up. If this field is not present, it is left to 
        Charge Point to decide how many times it wants to retry.
        - `retryInterval` (int): Optional. The interval in seconds after which a retry may be
         attempted. If this field is not present, it is left to Charge Point to decide how long 
         to wait between attempts.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class UnlockConnector_Req(OcppType):
    '''
    A class which describes the `UnlockConnector.Req` datatype in the OCPP documentation
    '''

    def __init__(self, connectorId:int):
        '''
        The main constructor to the `UnlockConnector_Req` class

        ## Description
        This contains the field definition of the UnlockConnector.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `connectorId` (int): Required. This contains the identifier of the connector to be 
        unlocked.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class GetCompositeSchedule_Req(OcppType):
    '''
    A class which describes the `GetCompositeSchedule.Req` datatype in the OCPP documentation
    '''

    def __init__(self, connectorId:int, duration:int, chargingRateUnit:ChargingRateUnitType):
        '''
        The main constructor to the `GetCompositeSchedule_Req` class

        ## Description
        This contains the field definition of the GetCompositeSchedule.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `connectorId` (int): Required. The ID of the Connector for which the schedule is requested.
        When ConnectorId=0, the Charge Point will calculate the expected consumption for the grid 
        connection.
        - `duration` (int): Required. Time in seconds. length of requested schedule.
        - `chargingRateUnit` (ChargingRateUnitType): Optional. Can be used to force a power or current profile
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class GetConfiguration_Req(OcppType):
    '''
    A class which describes the `GetConfiguration.Req` datatype in the OCPP documentation
    '''

    def __init__(self, key:List[str] = None):
        '''
        The main constructor to the `GetConfiguration_Req` class

        ## Description
        This contains the field definition of the GetConfiguration.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `key` (str): Required. Optional. List of keys for which the configuration value is requested.
        '''

        # Checking if the chargingSchedulePeriod is a list or not. 
        # Casting it to a list if its not 
        key = key if isinstance(key, list) else [key]

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class GetDiagnostics_Req(OcppType):
    '''
    A class which describes the `GetDiagnostics.Req` datatype in the OCPP documentation
    '''

    def __init__(self, location:str, retries:int = None, retryInterval:int = None, startTime:datetime.datetime = None, stopTime:datetime.datetime = None):
        '''
        The main constructor to the `GetDiagnostics_Req` class

        ## Description
        This contains the field definition of the GetDiagnostics.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `location` (str): Required. This contains the location (directory) where the diagnostics 
        file shall be uploaded to.
        - `retries` (str): Optional. This specifies how many times Charge Point must try to upload 
        the diagnostics before giving up. If this field is not present, it is left to Charge Point 
        to decide how many times it wants to retry.
        - `retryInterval` (int): Optional. The interval in seconds after which a retry may be attempted. 
        If this field is not present, it is left to Charge Point to decide how long to wait between attempts.
        - `startTime` (datetime.datetime): Optional. This contains the date and time of the oldest logging 
        information to include in the diagnostics.
        - `stopTime` (datetime.datetime): Optional. This contains the date and time of the latest logging
        information to include in the diagnostics.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)

class SendLocalList_Req(OcppType):
    '''
    A class which describes the `SendLocalList.Req` datatype in the OCPP documentation
    '''

    def __init__(self, listVersion:int, localAuthorizationList:AuthorizationData, updateType:UpdateType):
        '''
        The main constructor to the `SendLocalList_Req` class

        ## Description
        This contains the field definition of the SendLocalList.Req PDU sent by the Central 
        System to the Charge Point.

        ## Parameters
        - `listVersion` (int): Required. In case of a full update this is the version number 
        of the full list. In case of a differential update it is the version number of the 
        list after the update has been applied.
        - `localAuthorizationList` (AuthorizationData): Optional. In case of a full update 
        this contains the list of values that form the new local authorization list. In case 
        of a differential update it contains the changes to be applied to the local authorization 
        list in the Charge Point. Maximum number of AuthorizationData elements is available in the 
        configuration key: `SendLocalListMaxLength`
        - `updateType` (UpdateType): Required. This contains the type of update (full or differential) 
        of this request.
        '''

        accepted_args = {dictKey:dictValue for dictKey,dictValue in locals().items() if dictKey != 'self'}
        OcppType.__init__(self, **accepted_args)