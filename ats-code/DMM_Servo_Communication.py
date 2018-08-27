# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:55:13 2018
@author: henra
container for all low level functions required to work with the DMM servo drives
Using this library most functionality can be called with drive ID and appropriate data.

Useful function list
InitializeCommunication()    Must be called before initializing communication with servos
SetMainGain(driveID, gain)  
ReadMainGain(driveID) 
SetSpeedGain(driveID, gain)  
ReadSpeedGain(driveID)  
SetIntGain(driveID, gain) 
ReadIntGain(driveID) 
SetTrqCons(driveID, const) 
ReadTrqCons(driveID) 
SetHighSpeed(driveID, MaxSpeed)  
ReadHighSpeed(driveID) 
SetHighAccel(driveID, MaxAccel)    
ReadHighAccel(driveID)
SetPos_OnRange(driveID, OnRange)  
ReadPos_OnRange(driveID)  
SetPos_FoldNumber(driveID, gear)   
ReadPos_FoldNumber(driveID)
ConstSpeed(driveID, speed)   
SetDriveConfig(driveID, mode, encoder, servo, drive)    
ReadDriveConfig(driveID)  
ReadDriveStatus(driveID)  
GoRelativePosition(driveID, position) 
GoAbsPosition(driveID, position) 
"""

import numpy 
import os

#Function (Sent by host)
General_Read =          0x0e
Set_Origin =            0x00
Go_Absolute_Pos =       0x01
Make_LinearLine =       0x02
Go_Relative_Pos =       0x03
Make_CircularArc =      0x04            #define Go_Relative_PosM = 0x04
Assign_Driver_ID =      0x05
Read_Driver_ID =        0x06
Set_Driver_Config =     0x07
Read_Driver_Config =    0x08
Read_Driver_Status =    0x09
Turn_ConstSpeed =       0x0a
Square_Wave =           0x0b
Sin_Wave =              0x0c
SS_Frequency =          0x0d
Read_PosCmd32 =	      0x0e
Set_MainGain =          0x10
Set_SpeedGain =         0x11
Set_IntGain =           0x12
Set_TrqCons =           0x13
Set_HighSpeed =		 0x14
Set_HighAccel =		 0x15
Set_Pos_OnRange =       0x16
Set_FoldNumber =		 0x17
Read_MainGain =         0x18
Read_SpeedGain =        0x19
Read_IntGain =          0x1a
Read_TrqCons =          0x1b
Read_HighSpeed =    	 0x1c
Read_HighAccel =	      0x1d
Read_Pos_OnRange =      0x1e
Read_FoldNumber =	      0x1f

#functions (sent by driver)
Is_MainGain =           0x10
Is_SpeedGain =          0x11
Is_IntGain =            0x12
Is_TrqCons =            0x13
Is_HighSpeed =		 0x14
Is_HighAccel =		 0x15
Is_Driver_ID =		 0x16
Is_Pos_OnRange =        0x17
Is_FoldNumber =		 0x18
Is_Status =             0x19
Is_Config =             0x1a

#For driver status
Driver_OnPos =          0xfe
Driver_Busy =           0x01            #for b0
Driver_Servo =          0xfd
Driver_Free =           0x02            #for b1
Driver_Normal =         0x00
Driver_LostPhase =      0x04
Driver_OverCurrent =    0x08
Driver_OverHeat =       0x0c            #for b4 b3 b2 */
Driver_OverVolts =		 0x14
Is_AbsPos32 =			 0x1b		    #Absolute position 32
Is_TrqCurrent =		 0x1e		    #Motor current

#Following are used for Machine Code interpreting
Line_Error =	         0xff
Line_OK =				0x00
Motor_OnPos =			0x00
Motor_Busy =			0x01
Motor_Free =			0x02
Motor_Alarm =			0x03

# Drive ID's
stage1_drive_id = 10 # drive id for stage 1 servo drive that runs the stage 1 set of rollers
stage2_drive_id = 20 # drive id for stage 2 servo drive that runs the stage 2 set of rollers
radius_drive_id = 21 # drive id for the servo drive that controls the stage 2 platform that changes the bend radius of the machine
angle_drive_id = 22 # drive id for the servo drive that controls the angle of the entire stage 2 platform.
# the servo driven by this servo drive is attached to the rack and pinion on stage 2 of the machine
general_drive_id = 127



# ---------------------Functions for Testing--------------------------------------------------------

def binary_display_int(integer):
    '''
    Takes in an integer
    Returns the binary representation of the argument as a string
    A helpful tool to check the binary representation of an integer
    '''
    binary_number = bin(integer)[2:].zfill(8)
    # bin converts the integer to a binary string with 0b in front
    # using the [2:] reference we can just show what we want to see, 0's and 1's.
    return binary_number


def binary_display_byte(byte):
    '''
    Takes in a byte
    returns the binary representation of the arguement as a string
    A helpful tool to check the binary representation of a byte
    '''
    byte_as_integer = int.from_bytes(byte, byteorder='big', signed=True)
    # class method that takes in a byte and returns the integer
    # byte order needs to be big if you want the MSB on the left side. Byte order= little gives you MSB on the right.
    # the signed argument i# - if Brad can get servo read code working then we can display the servo parameters also ndicates whether two's complement is used to represent the integer

    binary_number = bin(byte_as_integer)[2:].zfill(8)
    # bin converts the integer to a binary string with 0b in front
    # using the [2:] reference we can just show what we want to see, 0's and 1's.

    return binary_number


# ------------------------------------------------------------------------------------------------

def InitializeCommunication():
    #initializes communication for raspberry pi
    global ser
    global IsPi
    IsPi = False
    
    try: 
        a=os.uname()[1]
    except:
        print('Error: unable to run on windows OS')
        a='0'
    print(a)
    
    if a == 'raspberrypi':
        IsPi = True
        import serial
    
    if IsPi == False:
        print('Error: code not running on Raspberry pi')
        return
    ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)

def DriveByte(a): #formats start byte properly pg 52
    #if this returns nothing then there is an error
    if a >= 0 and a <= 63:
        #if the drive ID is within the acceptable range
        return a
    elif a == 127:
        #if the drive ID is the general id no.
        return a
    else:
        #drive ID is not within the acceptable range of values
        print('Error: drive location out of acceptable range of values')

def FunctionAndLength(length,code): #formats 2nd byte pg53
    l = (length-1) * 32 #pg53, 32 is placeholder moving l to proper position
    output = 0x80 + l + code #0x80 adds 1000 0000 to the number
    return output

def OutData(num, function): #returns a list containing properly formatted integers to transmit data
    UnsignedFunctionCodes = {Assign_Driver_ID, Set_Driver_Config, Set_MainGain,
                             Set_SpeedGain, Set_IntGain, Set_TrqCons,
                             Set_HighSpeed, Set_HighAccel, Set_Pos_OnRange}
    if function in UnsignedFunctionCodes:
        output = (int(numpy.binary_repr(num,7),2) + 0x80,)
        return output

    Dummy = {Set_Origin, Read_Driver_ID, Read_Driver_Config, Read_Driver_Status,
             Read_MainGain, Read_SpeedGain, Read_IntGain, Read_TrqCons,
             Read_HighSpeed, Read_HighAccel, Read_Pos_OnRange, Read_FoldNumber}
    if function in Dummy:
        output = (0x8a,)
        return output
        
    if num >= 0 and num < 64:
        a = (int(numpy.binary_repr(num,7),2) + 0x80,)
        return a
    if num > 63  and num < 8192:
        a = int(numpy.binary_repr(num,14)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,14)[7:14],2) + 0x80
        output = (a,b)
        return output
    if num > 8191  and num < 1048576:
        a = int(numpy.binary_repr(num,21)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,21)[7:14],2) + 0x80
        c = int(numpy.binary_repr(num,21)[14:21],2) + 0x80
        output = (a,b,c)
        return output
    if num > 134217727:
        print('Error: input data out of range')
        return
    if num > 1048575:
        a = int(numpy.binary_repr(num,28)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,28)[7:14],2) + 0x80
        c = int(numpy.binary_repr(num,28)[14:21],2) + 0x80
        d = int(numpy.binary_repr(num,28)[21:28],2) + 0x80
        output = (a,b,c,d)
        return output

    if num < 0 and num > -65:
        a = (int(numpy.binary_repr(num,7),2) + 0x80,)
        return a
    if num <-64  and num > -8193:
        a = int(numpy.binary_repr(num,14)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,14)[7:14],2) + 0x80
        output = (a,b)
        return output
    if num <-8192  and num > -1048577:
        a = int(numpy.binary_repr(num,21)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,21)[7:14],2) + 0x80
        c = int(numpy.binary_repr(num,21)[14:21],2) + 0x80
        output = (a,b,c)
        return output
    if num <-134217728:
        print('Error: input data out of range')
        return
    if num <-1048576:
        a = int(numpy.binary_repr(num,28)[0:7],2) + 0x80
        b = int(numpy.binary_repr(num,28)[7:14],2) + 0x80
        c = int(numpy.binary_repr(num,28)[14:21],2) + 0x80
        d = int(numpy.binary_repr(num,28)[21:28],2) + 0x80
        output = (a,b,c,d)
        return output
    
def CheckSum(BnA, BnMinus1A, DatalistA): # see page 55
    '''
    :param BnA: none type
    :param BnMinus1A: int
    :param DatalistA: list
    :return:
    '''

    numData = len(DatalistA) #number of bytes used to transmit data   
    dataSum = 0
    for i in range(0,numData): # Calculates sum of data integers
        dataSum = dataSum + DatalistA[i]
    S = BnA + BnMinus1A + dataSum
    output = 0x80 + (S%128)
    return output

def Send(driveID, ToDo, packet): 
    #packet cannot be empty even if function code requests dummy variable
    '''
    :param driveID:
    :param ToDo:
    :param packet:
    :return:
    '''

    #packet should be integer not hex
    #Send packet to controller
    DataList = OutData(packet,ToDo)
    OutLen = len(DataList) #DataList is a tuple #of data bits see page 54 for how to set
    OutArray = bytearray(OutLen+3) # data to send to controller
    Bn = DriveByte(driveID)
    BnMinus1 = FunctionAndLength(OutLen, ToDo)
    B0 = CheckSum(Bn, BnMinus1, DataList)
    #assign variables to output byte array
    OutArray[0] = Bn
    OutArray[1] = BnMinus1
    a=2
    for i in DataList:
        OutArray[a] = i
        a=a+1
    OutArray[OutLen+2] = B0

    if IsPi == True:
        ser.write(OutArray)             
        ser.flush()                    
    else:
        print('Error: code not running on Pi or InitializeCommunication() not called')
    return OutArray

def Obtain(): #read from serial and pull out relevent info
    msg = ser.read(100)
    
    #Check for errors in transmission
    if ((sum(msg)-msg[-1])%128)+128 != msg[-1]:
        output = (False,'asdf','asdf','asdf')
        #Error found False = Receive()[0] please resend transimission
        return output
    
    servo = msg[0] #servo number of servo returning command
    function = int(bin(msg[1])[5:],2)  #function code of command
    dataBytes = int(bin(msg[1])[3:5],2) + 1 # number of bytes in data section of packet
    total = 0  #data contnained in transmission
    for i in range(2,2+dataBytes):
        total = total + (msg[i] - 0x80) * 2**(7*(2+dataBytes-i-1))
    
    # check function code to see if data should be unsigned
    UnsignedFunctionCodes = {Is_MainGain, Is_SpeedGain, Is_IntGain, Is_TrqCons, Is_HighSpeed,
                             Is_HighAccel, Is_Driver_ID, Is_Pos_OnRange, Is_Status, Is_Config, Is_FoldNumber}
    if function in UnsignedFunctionCodes:
        output = (True,servo,function,total)
        return output        
    
    signed = 0  
    #change to negative numbers if required
    if total >= 134217728 and dataBytes == 4:
        signed = total - 268435456
        output = (True,servo,function,signed) 
    elif total >= 1048576 and dataBytes == 3:
        signed = total - 2097152
        output = (True,servo,function,signed)
    elif total >= 8192 and dataBytes == 2:
        signed = total - 16384
        output = (True,servo,function,signed) 
    elif total >= 64 and dataBytes == 1:
        signed = total - 128
        output = (True,servo,function,signed)
    else:
        output = (True,servo,function,total)
    return output

# ------------------------ convenience functions ------------------------
# include all function codes on pg 53
    
def SetMainGain(driveID, gain):
    '''
    :param driveID: servo controller identification number
    :param gain: gain value to send to driveID
    '''
    
    Send(driveID, Set_MainGain, gain)
    output = ReadMainGain(driveID)
    return output
 
def ReadMainGain(driveID):
    '''
    :param driveID: servo controller identification number
    :return: Gain parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_MainGain, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def SetSpeedGain(driveID, gain):
    '''
    :param driveID: servo controller identification number
    :param gain: speed gain value to send to driveID
    '''
    
    Send(driveID, Set_SpeedGain, gain)
    output = ReadSpeedGain(driveID)
    return output

def ReadSpeedGain(driveID):
    '''
    :param driveID: servo controller identification number
    :return: speed Gain parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_SpeedGain, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def SetIntGain(driveID, gain):
    '''
    :param driveID: servo controller identification number
    :param gain: int gain value to send to driveID
    '''
    
    Send(driveID, Set_IntGain, gain)
    output = ReadIntGain(driveID)
    return output
  
def ReadIntGain(driveID):
    '''
    :param driveID: servo controller identification number
    :return: int Gain parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_IntGain, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3] 

def SetTrqCons(driveID, const):
    '''
    :param driveID: servo controller identification number
    :param const: torque const value to send to driveID
    '''
    
    Send(driveID, Set_TrqCons, const)
    output = ReadTrqCons(driveID)
    return output
  
def ReadTrqCons(driveID):
    '''
    :param driveID: servo controller identification number
    :return: torque const value to send to driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_TrqCons, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3] 

def SetHighSpeed(driveID, MaxSpeed):
    '''
    :param driveID: servo controller identification number
    :param MaxSpeed: MaxSpeed value to send to driveID
    '''
    
    Send(driveID, Set_HighSpeed, MaxSpeed)
    output = ReadHighSpeed(driveID)
    return output
 
def ReadHighSpeed(driveID):
    '''
    :param driveID: servo controller identification number
    :return: Gain parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_HighSpeed, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def SetHighAccel(driveID, MaxAccel):
    '''
    :param driveID: servo controller identification number
    :param MaxAccel: Maximum acceleration value to send to driveID
    '''
    
    Send(driveID, Set_HighAccel, MaxAccel)
    output = ReadHighAccel(driveID)
    return output

def ReadHighAccel(driveID):
    '''
    :param driveID: servo controller identification number
    :return: Gain parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_HighAccel, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def SetPos_OnRange(driveID, OnRange):
    '''
    :param driveID: servo controller identification number
    :param OnRange: position range value to send to driveID see page 44
    '''
    
    Send(driveID, Set_Pos_OnRange, OnRange)
    output = ReadPos_OnRange(driveID)
    return output

def ReadPos_OnRange(driveID):
    '''
    :param driveID: servo controller identification number
    :return: position range parameter for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_Pos_OnRange, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def SetPos_FoldNumber(driveID, gear):
    '''
    :param driveID: servo controller identification number
    :param gear: set gear number value to send to driveID see page 44
    '''
    if gear < 500 or gear > 16384:
        print('Error, gear number is out of range, packet sent anyway')
    Send(driveID, Set_FoldNumber, gear)
    output = ReadPos_FoldNumber(driveID)
    return output

def ReadPos_FoldNumber(driveID):
    '''
    :param driveID: servo controller identification number
    :return: gear number for input driveID
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_FoldNumber, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]

def ConstSpeed(driveID, speed):
    '''
    :param driveID: servo controller identification number
    :speed: RPM the servo is desired to turn at
    '''
    Send(driveID, Turn_ConstSpeed, speed)

def SetDriveConfig(driveID, mode, encoder, servo, drive):
    '''
    :param driveID: servo controller identification number
    :see page 56 for other parameters
    '''
    if drive == False:
        drive=0
    if drive == True:
        drive=1
    if encoder == False:
        encoder=0
    if encoder == True:
        encoder=1    
    data = 80 + drive * 32 + servo * 8 + encoder * 4 + mode   
    Send(driveID, Set_Driver_Config, data)

def ReadDriveConfig(driveID):
    '''
    :param driveID: servo controller identification number
    :return: integer tuple representing:communications mode, encoder setting, servo setting, and freerunning in that order
    :see page 56 for more details
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_Driver_Config, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    data = numpy.binary_repr(var[3],7) #see page 56
    mode = int(data[5:7],2)    # 0-RS232, 1-CW,CCW, 2-Pulse, 3-Analog
    encoder = int(data[4:5],2) # 0-relative mode, 1-absolute mode
    servo = int(data[2:4],2)   # 0-position, 1-speed, 2-torque
    drive = int(data[1:2,2])   # 0-servo hard, 1-servo spin freely
    output = (mode, encoder, servo, drive)
    return output
  
def ReadDriveStatus(driveID):
    '''
    :param driveID: servo controller identification number
    :return: integer tuple representing: onPosition, servo, alarm, motion in that order
    :see page 56 for more details
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_Driver_Status, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    data = numpy.binary_repr(var[3],7) #see page 56
    onPosition = int(data[6:7],2)  # 0-motor on position, 1-motor moving
    servo = int(data[5:6],2)       # 0-motor servo, 1-motor free
    alarm = int(data[2:5],2)       # 0-no alarm, 1-motor lost phase alarm, 2-motor current alarm, 3-motor overheat or overpower alarm, 4- error for CRC error check
    motion = int(data[1:2,2])      # 0- S curve, linear, circular motion completed, 1- Motor in middle of move
    output = (onPosition, servo, alarm, motion)
    return output

def GoRelativePosition(driveID, position):
    '''
    :param driveID: servo controller identification number
    :param position: position relative to current one to send drive to
    '''
    Send(driveID, Go_Relative_Pos, position)
      
def GoAbsPosition(driveID, position):
    '''
    :param driveID: servo controller identification number
    :param position: absolute position to send drive to
    '''
    Send(driveID, Go_Absolute_Pos, position)   
    
def AbsPosRead(driveID):
    '''
    :param driveID: servo controller identification number
    : ready absolute position
    '''
    i=0
    var = (False, 'asdf', 'asdf', 'asdf')
    while var[0] == False:
        Send(driveID, Read_PosCmd32, 0x5A)
        var = Obtain()
        i = i+1
        if i > 5:
            print('Error: variable not sent, set, or recieved properly, transmission error, checksum is not correct')
            break
    return var[3]
    
    
class Position():
    def __init__(self,driveID):
        # see if the serial port is initialized and if it isn't initialize it
        try:
            ser
        except NameError:  #serial port isn't open so open it
            InitializeCommunication() # function to open serial port
                   
        #getting saved values from controller
        self._DriveID = driveID
        self._MainGain = ReadMainGain(driveID)
        self._SpeedGain = ReadSpeedGain(driveID)
        self._IntGain = ReadIntGain(driveID)
        self._HighSpeed = ReadHighSpeed(driveID)
        self._HighAccel = ReadHighAccel(driveID)
        self._Pos_OnRange = ReadPos_OnRange(driveID)
        self._GearNum = ReadPos_FoldNumber(driveID)
        self._AbsPos = AbsPosRead(driveID)
        
    def SetOrigin(self): #sets current position to zero
        Send(self.driveID,Set_Origin,0x5e)
    
    def GoToRel(self,position): #go to a position specified relative to the current one
        GoRelativePosition(self.driveID, position)
        
    def RefreshPos(self): #refreshes the absolute position attributed by reading the servo
        self._AbsPos = AbsPosRead(self.driveID)
        return self._AbsPos
    
    def Stopped(self): #function that can be used to poll motor to determine if it is moving
        var = (False, 'asdf', 'asdf', 'asdf')
        Send(self.driveID, Read_Driver_Status, 0x5A)
        var = Obtain()
        data = numpy.binary_repr(var[3],7) #see page 56
        onPosition = int(data[6:7],2)  # 0-motor on position, 1-motor moving
        if onPosition == 0:
            return True
        if onPosition == 1:
            return False
             
    def getabspos(self): #calls the absolute position variable as is without checking
        return self._AbsPos
    
    def setabspos(self,position):
        GoAbsPosition(self.driveID, position)
        self._AbsPos = position
        
    AbsPos = property(getabspos, setabspos,fdel=None,'Absolute position of position servo')
    
    def RefreshMainGain(self): #asks servo controller for gain value
        self._MainGain = ReadMainGain(self.driveID)
        return self._MainGain
    
    def getmaingain(self): #returns value of gain stored in memory
        return self._MainGain
    
    def setmaingain(self,gain): #sets main gain and assigns the input value to the controller
        if gain > 127 or gain < 0:
            print('Gain value out of range')
            return self._MainGain
        self._MainGain = SetMainGain(self.driveID, gain)
        return self._MainGain
    
    MainGain = property(getmaingain, setmaingain, fdel=None, 'Main Gain')
    #if main gain function works expand for other variables