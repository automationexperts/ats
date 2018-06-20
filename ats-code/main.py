import time
import sys
import serial
from RPi import GPIO
import binascii

#display the version of python being used.
print("Sytem Version:")
print (sys.version)


#BACKGROUND INFO
#   for this script to work the Rx and Tx pins on the raspberry pi must be
#   connected to one another. This is also known as an RS232 Loopback test

def checkopen():
    if ser.is_open == True:
        print("Connection is open")
    elif ser.is_open == False:
        print("Connection is closed")
    pass


#FUNCTIONS
def convert_bytes_to_listint(byte):
    '''
    Pass in a byte literal of type "bytes". This type may contain ASCII characters.
    This function returns that byte literal broken up into a list and converted into integer values from 0 to 255.
    '''
    bytelist = list(byte)
    return bytelist


#CONNECTION SETUP
print(sys.version)
#ser = serial.Serial("/dev/ttyAMA0", baudrate =  38400, timeout = 1000)
#note that /dev/serial0 brings up the default serial port whereas ttyAMA0
#attempts to access the UART used for the bluetooth on the raspberry pi 3
ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2)
print(ser.name)
print("Baudrate = {b}".format(b=ser.baudrate))

#CAN USE THIS FOR SETTING BAUDRATE AFTER CONNECTION IS SETUP
#ser.baudrate = 38400
#print("Baudrate = {b}".format(b=ser.baudrate))

#OPEN CONNECTION AND CHECK
checkopen()


#read one character
#msga = ser.read()

#read 100 characters and store it in str msg
msg = ser.read(100)

#print the string msg
print(msg)

#print the type of msg
print(type(msg))


#CLOSE CONNECTION AND CHECK
ser.close()
checkopen()

#Test code. Convert bytes to hexadecimal.
print(convert_bytes_to_listint(msg))



#-------------------------------------------------------------------------------


#DMM variables

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
Read_PosCmd32 =	        0x0e
Set_MainGain =          0x10
Set_SpeedGain =         0x11
Set_IntGain =           0x12
Set_TrqCons =           0x13
Set_HighSpeed =			0x14
Set_HighAccel =			0x15
Set_Pos_OnRange =       0x16
Set_FoldNumber =		0x17
Read_MainGain =         0x18
Read_SpeedGain =        0x19
Read_IntGain =          0x1a
Read_TrqCons =          0x1b
Read_HighSpeed =    	0x1c
Read_HighAccel =	    0x1d
Read_Pos_OnRange =      0x1e
Read_FoldNumber =	    0x1f

#functions (sent by driver)
Is_MainGain =           0x10
Is_SpeedGain =          0x11
Is_IntGain =            0x12
Is_TrqCons =            0x13
Is_HighSpeed =			0x14
Is_HighAccel =			0x15
Is_Driver_ID =			0x16
Is_Pos_OnRange =        0x17
Is_FoldNumber =			0x18
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
Driver_OverVolts =		0x14
Is_AbsPos32 =			0x1b		    #Absolute position 32
Is_TrqCurrent =			0x1e		    #Motor current

#Following are used for Machine Code interpreting
Line_Error =			0xff
Line_OK =				0x00
Motor_OnPos =			0x00
Motor_Busy =			0x01
Motor_Free =			0x02
Motor_Alarm =			0x03