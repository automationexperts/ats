# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:55:13 2018

@author: henra
"""

import time
import sys
import serial
from RPi import GPIO
import binascii

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

# Drive ID's
stage1_drive_id = 10 # drive id for stage 1 servo drive that runs the stage 1 set of rollers
stage2_drive_id = 20 # drive id for stage 2 servo drive that runs the stage 2 set of rollers
radius_drive_id = 21 # drive id for the servo drive that controls
# the stage 2 platform that changes the bend radius of the machine
angle_drive_id = 22 # drive id for the servo drive that controls
# the angle of the entire stage 2 platform.
# the servo driven by this servo drive is attached to the rack and pinion on stage 2 of the machine

def DriveByte(a): #formats start byte properly pg 52
    #if this returns nothing then there is an error
    if a >= 0 and a <= 63: 
        return a

def FunctionAndLength(length,code): #formats 2nd byte pg53
    l = (length-1) * 32 #pg53, 32 is placeholder moving l to proper position
    output = 0x80 + l + code
    return output

def OutData(data): #returns a list containing properly formatted integers to transmit data
    # input data must be a large integer we want to transmit
    BinData = bin(data)[2:] #converts input integer to binary string and chops off 0b
    length = len(BinData)   #number of binary digits in data
    b = divmod(length,7)
    if b[1] == 0: #if modulus is 0 number is exactly divisible
        a = b[0]
    else:
        a = b[0] + 1
    numbyte=int(a) # number of bytes required to send data
    if numbyte > 4:
        return
    
    outlist=list()
    outlist.append(int(BinData[0:b[1]],2) + 0x80)
    for i in range(1,numbyte):
        start = b[1] + (i-1) * 7
        end   = b[1] + i * 7
        outlist.append(int(BinData[start:end],2) + 0x80)
    return outlist

def OutputSize(data): #notice how function is very similar to OutData, 
    BinData = bin(data)[2:] #converts input integer to binary string and chops off 0b
    length = len(BinData)   #number of binary digits in data
    b = divmod(length,7)
    if b[1] == 0: #if modulus is 0 number is exactly divisible
        a = b[0]
    else:
        a = b[0] + 1
    numbyte=int(a) # number of bytes required to send data
    if numbyte > 4:
        return
    else:
        return numbyte
    
def CheckSum(BnA, BnMinus1A, DatalistA): # see page 55
    numData = len(DatalistA) #number of bytes used to transmit data   
    dataSum = 0
    for i in range(0,numData): # Calculates sum of data integers
        dataSum = dataSum + DatalistA[i]
    S = BnA + BnMinus1A +dataSum
    output = 0x80 + (S%128)
    return output
        

# Start of Send code -------------------------------------------------------

# initialize the pi's serial port to controller parameters
# page 50 of controller manual
#ser = serial.Serial("/dev/serial0")  #this is the only serial port we use on the pi
#ser.baudrate = 38400
#ser.timeout = 2
#ser.PARITY_NONE
#ser.STOPBITS_ONE
#ser.EIGHTBITS

#set the varibles below
driveID = radius_drive_id
ToDo = 0x1a #packet function code see page 53
packet = 0x14b5 #data to be sent
OutLen = OutputSize(packet) #of data bits see page 54 for how to set

OutArray = bytearray(OutLen+3) # data to send to controller
Bn = DriveByte(driveID)
BnMinus1 = FunctionAndLength(OutLen, ToDo)
DataList = OutData(packet) 
B0 = CheckSum(Bn, BnMinus1, DataList)

#assign variables to output byte array
OutArray[0] = Bn.to_bytes(1,'big')
OutArray[1] = BnMinus1.to_bytes(1,'big')
for i in range(2,OutLen+3):
    a = DataList[i-2]
    OutArray[i] = a.to_bytes(1,'big')
OutArray[OutLen+3] = B0.to_bytes(1,'big')

#OutArray is now ready to be passed out to servo controller
#ser.write(OutArray)
#ser.flush()

# End of Send code ---------------------------------------------------------