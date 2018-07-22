# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:55:13 2018

@author: henra
"""

import time
import sys
import serial
import numpy #unable to install numpy to the raspberry pi
from RPi import GPIO
import binascii
import math
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
Read_PosCmd32 =	        0x0e
Set_MainGain =          0x10
Set_SpeedGain =         0x11
Set_IntGain =           0x12
Set_TrqCons =           0x13
Set_HighSpeed =		    	0x14
Set_HighAccel =		    	0x15
Set_Pos_OnRange =       0x16
Set_FoldNumber =		  0x17
Read_MainGain =         0x18
Read_SpeedGain =        0x19
Read_IntGain =          0x1a
Read_TrqCons =          0x1b
Read_HighSpeed =    	  0x1c
Read_HighAccel =	     0x1d
Read_Pos_OnRange =      0x1e
Read_FoldNumber =	     0x1f

#functions (sent by driver)
Is_MainGain =           0x10
Is_SpeedGain =          0x11
Is_IntGain =            0x12
Is_TrqCons =            0x13
Is_HighSpeed =			  0x14
Is_HighAccel =			  0x15
Is_Driver_ID =			  0x16
Is_Pos_OnRange =        0x17
Is_FoldNumber =			  0x18
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
Driver_OverVolts =		  0x14
Is_AbsPos32 =			  0x1b		    #Absolute position 32
Is_TrqCurrent =			  0x1e		    #Motor current

#Following are used for Machine Code interpreting
Line_Error =			   0xff
Line_OK =				   0x00
Motor_OnPos =			0x00
Motor_Busy =			   0x01
Motor_Free =			   0x02
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
    # the signed argument indicates whether two's complement is used to represent the integer

    binary_number = bin(byte_as_integer)[2:].zfill(8)
    # bin converts the integer to a binary string with 0b in front
    # using the [2:] reference we can just show what we want to see, 0's and 1's.

    return binary_number


# ------------------------------------------------------------------------------------------------

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

def int2ControllerFormat(num):
    #import numpy
    #make sure 'import numpy' is at top of file
    if num >= 0 and num < 64:
        output = int(numpy.binary_repr(num,7),2)
        return output
    if num >= 64 and num < 8192:
        output = int(numpy.binary_repr(num,14),2)
        return output
    if num >= 8192 and num < 1048576:
        output = int(numpy.binary_repr(num,21),2)
        return output
    if num >= 1048576 and num < 134217728:
        output = int(numpy.binary_repr(num,28),2)
        return output
    if num >= 134217728:
        print('error, input data out of range')
        return

    if num < 0 and num >= -64:
        output = int(numpy.binary_repr(num,7),2)
        return output
    if num <-64 and num >= -8192:
        output = int(numpy.binary_repr(num,14),2)
        return output
    if num <-8192 and num >= -1048576:
        output = int(numpy.binary_repr(num,21),2)
        return output
    if num <-1048576 and num >= -134217728:
        output = int(numpy.binary_repr(num,28),2)
        return output
    if num <-134217728:
        print('error, input data out of range')
        return

def OutData(data): #returns a list containing properly formatted integers to transmit data
    # input data must be a large integer we want to transmit
    #In C data is sent out without adjusting for negative numbers so make sure
    #python is representing data the same as C represents an integer
    #Incoming data is interpreted using Cal_SignValue or Cal_Value, both 
    #functions do the same thing.

    BinData = bin(int2ControllerFormat(data))[2:] #converts input integer to binary string and chops off 0b
    length = len(BinData)   #number of binary digits in data
    b = divmod(length,7)
    outlist = list()
    
    if (length == 7 or length == 14 or length == 21 or length == 28) and BinData[0] == '1':  #number is negative
       numbyte = int(b[0]) # number of bytes required to send data
       for i in range(0,numbyte):
           start = b[1] + (i) * 7
           end = b[1] +(i+1) * 7
           outlist.append(int(BinData[start:end],2) + 0x80)
       return outlist

    else:
       numbyte=int(b[0]+1) # number of bytes required to send data
    
    if numbyte > 4:
        print('Error: data too large to be sent')
        return
        
    if b[1] != 0: #append partial start byte to the beginning of BinData
        outlist.append(int(BinData[0:b[1]],2) + 0x80)  
        for i in range(1,numbyte):
            start = b[1] + (i-1) * 7
            end   = b[1] + (i) * 7
            outlist.append(int(BinData[start:end],2) + 0x80)
        return outlist
        
    if b[1] == 0:
        outlist.append(0x80) #need a leading blank byte see example 3 pg 62
        for i in range(0,numbyte-1):
            start = b[1] + (i) * 7
            end = b[1] +(i+1) * 7
            outlist.append(int(BinData[start:end],2) + 0x80)
        return outlist

def OutputSize(data): #notice how function is very similar to OutData, 
    BinData = bin(int2ControllerFormat(data))[2:] #converts input integer to binary string and chops off 0b
    length = len(BinData)   #number of binary digits in data

    #figure out how many bytes are in the data
    b = divmod(length,7)

    if (length == 7 or length == 14 or length == 21 or length == 28) and BinData[0] == '1':  #number is negative
       numbyte=int(b[0]) # number of bytes required to send data 
    else:
       numbyte=int(b[0]+1) # number of bytes required to send data

    # check if the data meets the criteria of being less than equal to 4 packets.
    # If it meets the criteria return the data, if not then return an error.
    if numbyte > 4:
        print('Error: data too large to be sent')
        return
    else:
        return numbyte
    
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
    '''

    :param driveID:
    :param ToDo:
    :param packet:
    :return:
    '''

    #packet should be integer not hex
    #Send packet to controller
    OutLen = OutputSize(packet) #of data bits see page 54 for how to set
    OutArray = bytearray(OutLen+3) # data to send to controller
    Bn = DriveByte(driveID)
    BnMinus1 = FunctionAndLength(OutLen, ToDo)
    DataList = OutData(packet) 
    B0 = CheckSum(Bn, BnMinus1, DataList)

    #assign variables to output byte array
    OutArray[0] = Bn
    OutArray[1] = BnMinus1
    for i in range(2,OutLen+2):
        a = DataList[i-2]
        OutArray[i] = a
    OutArray[OutLen+2] = B0
    ser.write(OutArray)
    ser.flush()
    return OutArray

# MACHINE CHARACTERISTICS ---------------------------- [START]

#gearbox ratios
stage1_gear_ratio = 60 #gear ratio for gearbox that drives stage 1 rollers
stage2_gear_ratio = 60 #gear ratio for gearbox that drives stage 2 rollers
radius_gear_ratio = 40 #gear ratio for gearbox that drives stage 2 sled that adjusts the bend radius
angle_gear_ratio = 32 #gear ratio for the gearbox that adjusts the angle of stage 2

#define roller diameter in inches
roller_diameter = 10.0

#ballscrew lead in mm
# LEAD refers to the distance traveled for each complete turn of the screw
ballscrew_lead = 5 #mm

# MACHINE CHARACTERISTICS ---------------------------- [END]



#define variable for linear speed in m/min.
#default value is 1.0 m/min
linear_speed = 1.0
#stage1_rpm = get_rpm(linear_speed,roller_diameter,stage1_gear_ratio)
#stage2_rpm = get_rpm(linear_speed,roller_diameter,stage2_gear_ratio)



# High Level Functions [Start] -------------------------------------------------------


def get_rpm(s,D,R):
    '''
    :param s: desired linear speed in m/min that the machine will process profiles
    :param D: diameter of the roller in inches
    :param R: gear ratio of the relative gearbox driving the rollers
    :return: gets rpm of motor rounded to the nearest integer that the motor needs to turn at to meet the desired linear speed
    '''

    rpm = R*s*1000/(math.pi*D*25.4)
    #print("Linear Speed is",s,"m/min")
    #print("RPM of motor is",round(rpm),"rpm")

    return int(round(rpm))

def set_linear_speed():
    global linear_speed
    global menu_items
    a = input("Input linear process speed of profile (m/min) (+'ve for forward through the machine, -'ve for reverse):")
    linear_speed = float(a)
    print("linear_speed",linear_speed)
    menu_items = generate_menu_items()
    return

def generate_menu_items():
    a = {"0":[0,"Stop All Rollers",stop_all],
                  "1":[1,"Start Stage 1 Rollers",stage1_start,get_rpm(linear_speed,roller_diameter,stage1_gear_ratio)],
                  "2":[2,"Start Stage 2 Rollers",stage2_start,get_rpm(linear_speed,roller_diameter,stage2_gear_ratio)],
                  "3":[3,"Set Linear Speed (m/min)",set_linear_speed]}
    return a

def stage1_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage1_drive_id,Turn_ConstSpeed,rpm)
    Send(general_drive_id, Turn_ConstSpeed, rpm)
    print("Stage 1 Started at",rpm,"rpm")
    return

def stage2_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage2_drive_id,Turn_ConstSpeed,rpm)
    Send(general_drive_id, Turn_ConstSpeed, rpm)
    print("Stage 2 Started at",rpm,"rpm")
    return

def stop_all():
    '''

    :return:
    '''

    Send(stage1_drive_id,Turn_ConstSpeed,0)
    Send(stage2_drive_id,Turn_ConstSpeed,0)
    Send(radius_drive_id,Turn_ConstSpeed,0)
    Send(angle_drive_id,Turn_ConstSpeed,0)
    print("All drives stopped")
    return

def move_Raxis(d):
    '''
    :param d:
    :return:
    '''
    #d is the distance in mm, positive or negative that you want the r-axis
    #Send(radius_drive_id,Go_Relative_Pos,steps)

    return

def gear_ratio(gear_num):
    return 4096/gear_num

def max_motor_speed(k,gear_ratio):
    '''

    :param k: can be an integer from 1 to 127. Max Acceleration parameter that should be read from the servo drive using
    the Read_HighAccel function code.

    :param gear_ratio: use gear_ratio(gear_num) function to calculate this

    :return: Returns the maximum speed of the motor in rpm
    '''

    maxspeed = (1/16)*(k+3)*(k+3)*12.21*gear_ratio
    return maxspeed

def max_motor_acceleration(k,gear_ratio):
    '''

    :param k: can be an integer from 1 to 127. Max Acceleration parameter that should be read from the servo drive using
    the Read_HighAccel function code.

    :param gear_ratio: use gear_ratio(gear_num) function to calculate this

    :return: Returns the acceleration of the motor in rpm/s
    '''

    maxacceleration = k*635.78*gear_ratio
    return maxacceleration




# High Level Functions [End] -------------------------------------------------------


# Operating System Functions [Start] -----------------------------------------------------

#Create a list of menu items/commands for the user to use
#The key will be the option number displayed on the HMI (human machine interface)
#The first item in the Dictionary list is the number of the command
#The second item in the list is the function name without parenthesis ()
#The third, fourth, fifth, and so on items in the list should be the arguments passed into the function
menu_items = generate_menu_items()

#create a list of the keys so that we can validate if the input is valid
menu_keys = menu_items.keys()


def clear():
    '''
    Clears the Raspberry Pi Console Screen
    :return:
    '''
    os.system("clear")
    return

def hmi_display(menu_items):
    '''

    :return:
    '''

    #clear()
    print("Linear Speed (of profile)\t",linear_speed,"m/min")
    print("STAGE 1 RPM\t\t\t",get_rpm(linear_speed,roller_diameter,stage1_gear_ratio),"rpm")
    print("STAGE 2 RPM\t\t\t",get_rpm(linear_speed,roller_diameter,stage2_gear_ratio),"rpm")
    print("\n")
    print("Command Options")

    for i in range(0, len(menu_items)):
        print(i, "-", menu_items[str(i)][1])

    print("exit - exits the program")

    return


def execute_command(a):
    '''
    Executes the appropriate command when passed a list from menu_items
    :return:
    '''

    #check how many items in menu_items to see if there are any arguments for the function we want to call
    if len(menu_items[a]) == 3:
        #if no arguments, execute the command in cell 2 of the list in the dictionary
        menu_items[a][2]()
    elif len(menu_items[a]) == 4:
        # if 1 argument, execute the command in cell 2 of the list in the dictionary and pass the single argument
        print("4")
        menu_items[a][2](menu_items[a][3])
    else:
        print("Error: menu_items - dictionary cell (list) length does not match an expected value")

    return

#sample code for running a function from user input
#def testfunction():
#    print("it worked!")
#    return

#ommands = {'0':["this is my test function description",testfunction]}

#cmd = input("Choose a command:")

#print(commands[cmd][0])
#commands[cmd][1]()



# Operating System Functions [End] -------------------------------------------------------


# Start of Send code -------------------------------------------------------

# initialize the pi's serial port to controller parameters
# page 50 of controller manual
ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)  #this is the only serial port we use on the pi
#ser.baudrate = 38400
#ser.timeout = 2
#ser.PARITY_NONE
#ser.STOPBITS_ONE
#ser.EIGHTBITS

#PACKET DEFINITION
#DRIVE ID, FUNCTION CODE, AND DATA
#set the varibles below to set the data that will be sent.
driveID = general_drive_id
FunctionCode = Read_FoldNumber #packet function code see page 53. Function Code
data = 1 #data to be sent. Data can be max speed, gear number, etc.

ToController = Send(driveID, FunctionCode, data)
#everything works, packets are sent properly, negative numbers may need to 
#be properly formatted

#Sends Binary output to console for debugging purposes
print(ToController)
for a in ToController:
    print(binary_display_int(a))

#read 100 characters and store it in str msg
print("message read")                    #uncomment me
msg = ser.read(1000)                    #uncomment me

#print the string msg
print(msg)                    #uncomment me

# End of Send code ---------------------------------------------------------

# Main Program [START] -----------------------------------------------------

while True:

    hmi_display(menu_items)

    command = input("Input Command:")

    if command == "exit":
        break
    elif command in menu_keys:
        execute_command(command)
    else:
        continue

# Main Program [END] -----------------------------------------------------


# NOTES
#2018-07-15, 11:30
#forward and reverse turn constant speed works fine
#setting a value for 0 for turn constant speed does not work

#2018-07-15 12:55
#fixed a the problem where a value for 0 for turn constant speed did not work
#this now stops the motor
#issue was a > 0 operator instead of a >= 0 in the int2ControllerFormat function

#how many steps in a full revolution???
#n = steps in a full revolution
#n = 16384/Gear_Ratio or n = 4*Gear_Num

#2018-07-15 23:53
#something odd about the Read_FoldNum command. When you send this command the servo sends back some data
#typically the data that is received is 7 packets.
#B6 B6 B5 B4 B3 B2 B1 B0
#B6 is drive ID
#B5 is number of packets and function code
#B4 and B3 represent the 4*Line_Num
#B2 and B1 contain the Gear_Num
#B0 is check sum

#2018-07-20 00:12
#added hmi_display functionality for displaying a screen with current status and menu options for user to interact with
#added menu items/commands to a dictionary
#added user input and input validation
#added functionality to execute commands based on user input

#2018-07-22 8:00
#goal for today is to:
# - set linear speed
# - set forward/reverse or be able to reverse the roller movement in some way
# - get r-axis moving +'ve and -'ve in mm, translate mm to turns of the servo
# - get theta-axis moving +'ve and -'ve in degrees, translate degrees to turns of the servo
# - if Brad can get servo read code working then we can display the servo parameters also and introduce an initialization section of the code to grab those parameters

