# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 11:55:13 2018

@author: henra
"""

import time
import sys
import serial          #uncomment me to run on pi
import numpy #unable to install numpy to the raspberry pi
from RPi import GPIO   #uncomment me to run on pi
import binascii
import math
import os
import DMM_Servo_Communication as com


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
Set_HighSpeed =		   0x14
Set_HighAccel =		   0x15
Set_Pos_OnRange =       0x16
Set_FoldNumber =		   0x17
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
Line_Error =	        0xff
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

def OutData(num): #returns a list containing properly formatted integers to transmit data
    # input data must be a large integer we want to transmit
    #In C data is sent out without adjusting for negative numbers so make sure
    #python is representing data the same as C represents an integer
    #Incoming data is interpreted using Cal_SignValue or Cal_Value, both 
    #functions do the same thing.

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
        print('error, input data out of range')
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
        print('error, input data out of range')
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
    '''

    :param driveID: int type containing the drive ID number
    :param ToDo: int type pertaining to the function code
    :param packet: the data that you wish to have transmitted
    
    :return:
    '''
    
    #Brad to update the send command.


    #packet should be integer not hex
    #Send packet to controller
    DataList = OutData(packet)
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

    ser.write(OutArray)             #uncomment me to run on pi
    ser.flush()                     #uncomment me to run on pi
    
    #display the output
    print("Displaying Output of Send()")
    for a in OutArray:
        print(binary_display_int(a))
    print("\n")
    
    return OutArray

def Obtain():
    '''
    
    Read from serial and pull out relevent info.
    Output: Type is tuple with 4 integers 
    1st bit: true/false if there was an error transmitting
    2nd bit: id number
    3rd bit: function code
    4th bit: data
    
    '''
    
    
    msg = ser.read(100)                 #uncomment me to run on pi
    
    #check that something was sent
    if len(msg) == 0:
        #no mesage detected so check again
        output = (False,'asdf','asdf','asdf')
        return output
    
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
                             Is_HighAccel, Is_Driver_ID, Is_Pos_OnRange, Is_Status, Is_Config}
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


# MACHINE CHARACTERISTICS ---------------------------- [START]

#gearbox ratios
stage1_gear_ratio = 60 #gear ratio for gearbox that drives stage 1 rollers
stage2_gear_ratio = 60 #gear ratio for gearbox that drives stage 2 rollers
radius_gear_ratio = 40 #gear ratio for gearbox that drives stage 2 sled that adjusts the bend radius
theta_gear_ratio = 32 #gear ratio for the gearbox that adjusts the angle of stage 2

#define roller diameter in inches
roller_diameter = 10.0

#distance between the two fixed rollers in stage 2 in m
roller_distance = 600/1000

#ballscrew lead in mm
# LEAD refers to the distance traveled for each complete turn of the screw
ballscrew_lead = 5 #mm

#theta-axis information
n_rack = 350 #number of teeth on the curved rack (in one complete revolution)
n_pinion = 12 #number of teeth on the pinion spur gear

#the slope between theta and r-axis.
#ie. theta (deg) / r (m) = 0.38119333
xtslope = 0.38119333

# MACHINE CHARACTERISTICS ---------------------------- [END]


Send(21,Turn_ConstSpeed,100)


# INITIALIZATION ---------------------------- [START]

#BRAD'S code for initializing servos
taxis = com.Position(angle_drive_id)
raxis = com.Position(radius_drive_id)
#stage1 = com.Position(stage1_drive_id)
#stage2 = com.Position(stage2_drive_id)

raxis.sethighspeed(40)
raxis.sethighacl(16)
taxis.sethighspeed(12)
taxis.sethighacl(6)

print(raxis.GearNum)
print(taxis.GearNum)

#define variable for linear speed in m/min.
#default value is 1.0 m/min
linear_speed = 1.0 #m/min
radius_curvature = 1.5 #15.240 #m
R_gear_num = 4096 #gear_num parameter for the r-axis servo
T_gear_num = 4096 #gear_num parameter for the theta-axis servo
stage1_gear_num = 4096 #gear_num parameter for the stage 1 servo
stage2_gear_num = 4096 #gear_num parameter for the stage 2 servo
#gear number is from 500 to 16384



#default values for max speed and max acceleration
#valid values are between 1 and 127 (integer)
#these values should be read in in the initalization period once we have the read functionality working
k_stage1_mAcc = 2
k_stage2_mAcc = 2
k_radius_mAcc = raxis.gethighacl()
k_theta_mAcc = taxis.gethighacl()

k_stage1_mSpeed = 50
k_stage2_mSpeed = 50
k_radius_mSpeed = raxis.gethighspeed()
k_theta_mSpeed = taxis.gethighspeed()

last_action = "N/A"





# INITIALIZATION ---------------------------- [END]


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
    print("\n+'ve for forward through the machine, -'ve for reverse")
    a = input("Input linear process speed of profile (m/min): ")
    linear_speed = float(a)
    
    #menu_items = generate_menu_items()
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Linear Speed Set to: " + str(linear_speed) + " m/min"
    
    return

def set_radius():
    '''
    Sets the radius of curvature
    
    '''
    
    units = None
    
    while units != 1 and units !=2:
        print("1. metres")
        print("2. feet")
        units = int(input("What units would you like to use for Radius of Curvature?"))

    if units == 1:
        r = float(input("Radius of Curvature (m):"))
    elif units == 2:
        r = float(input("Radius of Curvature (ft):"))
        r = r*12*25.4/1000
    
    global radius_curvature
    radius_curvature = r
    
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Radius of Curavture Set to: " + str(radius_curvature) + " m (" + str(radius_curvature*1000/25.4/12) + " ft)"
    
    return

def generate_menu_items():
    a = {"0":[0,"Stop All Rollers",stop_all],
         "1":[1,"Start Stage 1 Rollers",stage1_start,get_rpm(linear_speed,roller_diameter,stage1_gear_ratio)],
         "2":[2,"Start Stage 2 Rollers",stage2_start,get_rpm(linear_speed,roller_diameter,stage2_gear_ratio)],
         "3":[3,"Set Linear Speed (m/min)",set_linear_speed],
         "4":[4,"Set Radius of Curvature (m)",set_radius],
         "5":[5,"Move R-Axis (mm)",move_Raxis],
         "6":[6,"Move Theta-Axis (deg)",move_Taxis],
         "7":[7,"Set Zero Position",zero],
         "8":[8,"Move to Curving Position",move_Curve]}
    return a

def stage1_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage1_drive_id,Turn_ConstSpeed,rpm)
    #Send(general_drive_id, Turn_ConstSpeed, rpm)
    Send(radius_drive_id, Turn_ConstSpeed, rpm)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Stage 1 Started at " + str(rpm) + " rpm"
    
    return

def stage2_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage2_drive_id,Turn_ConstSpeed,rpm)
    #Send(general_drive_id, Turn_ConstSpeed, rpm)
    Send(angle_drive_id,Turn_ConstSpeed,rpm)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Stage 2 Started at " + str(rpm) + " rpm"
    
    return

def stop_all():
    '''

    :return:
    '''

    Send(stage1_drive_id,Turn_ConstSpeed,0)
    Send(stage2_drive_id,Turn_ConstSpeed,0)
    Send(radius_drive_id,Turn_ConstSpeed,0)
    Send(angle_drive_id,Turn_ConstSpeed,0)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "All drives stopped."
    return

def move_Raxis():
    '''
    :param d:
    :return:
    '''
    #d is the distance in mm, positive or negative that you want the r-axis
    #Send(radius_drive_id,Go_Relative_Pos,steps)

    print("\n")
    print("+'ve: smaller radius of curvature, -'ve: larger radius of curvature")

    d = float(input("Distance to move R-Axis (mm):"))
    spr = 4 * R_gear_num  # steps per revolution
    steps = d/ballscrew_lead*spr*radius_gear_ratio
    send_steps = int(round(steps))

    print(steps)
    print(int(round(steps)))

    Send(radius_drive_id,Go_Relative_Pos,send_steps)
    
    #z=Obtain()
    #print(z)
    

    # how many steps in a full revolution???
    # n = steps in a full revolution
    # n = 16384/Gear_Ratio or n = 4*Gear_Num
    
    #set last_action message on hmi screen
    global last_action
    last_action = "R-axis moved by: " + str(d) + " mm, " + str(send_steps/spr) + " servo revs, " + str(send_steps) + " steps"

    return

def move_Taxis():
    '''
    Takes float input in units of degrees. Moves the theta axis by a number of
    degrees that is taken in by the function.
    
    :return: nothing
    '''
    #d is the distance in mm, positive or negative that you want the r-axis
    #Send(radius_drive_id,Go_Relative_Pos,steps)

    print("\n")
    print("+'ve: more curvature in the profile, -'ve: straighter profile")

    theta = float(input("Angle to move Theta-Axis (deg):"))
    spr = 4 * T_gear_num  # steps per revolution for theta-axis servo
    steps = spr * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps = int(round(steps))

    print(steps)
    print(int(round(steps)))

    Send(angle_drive_id,Go_Relative_Pos,send_steps)

    # how many steps in a full revolution???
    # n = steps in a full revolution
    # n = 16384/Gear_Ratio or n = 4*Gear_Num
    
    #set last_action message on hmi screen
    global last_action
    last_action = "T-axis moved by: " + str(theta) + " degrees, " + str(send_steps/spr) + " servo revs, " + str(send_steps) + " steps"

    return

def zero():
    '''
    :sets the raxis and taxis to a zero or origin point
    '''
    raxis.SetOrigin()
    taxis.SetOrigin()
    
    global last_action
    last_action = "radius and theta axes set to zero at current position"    
    
     #for later on when we incorporate a proximity sensor
    #com.ConstSpeed(raxis.driveID,60) #move servo closer to the sensor
    #com.ConstSpeed(thetaxis.driveID,60)
    #while (radlimit == false):
        #test GPIO to determine when radlimit becomes true
    #com.ConstSpeed(raxis.driveID,0)
    #com.ConstSpeed(thetaxis.driveID,0)
    #raxis.SetOrigin()
    #thetaxis.SetOrigin()  
    
    return   

    


def move_Curve():
    '''
    Takes in radius of curvature (m)
    
    :return: nothing
    
    '''

    #radius of curvature in m
    R = radius_curvature
    
    #roller radius in m
    r = roller_diameter/2*25.4/1000
    
    #distance between rollers in m
    d = roller_distance
    
    print("radius of curvature (m) = ", R)
    
    #calculate the r-axis movement (labelled x here) in meters
    x = R - (-1*(d - 2*r - 2*R)*R**2*(r + R)**2*(d + 2*r + 2*R))**0.5/(2*(r + R)**2)
    
    #x = R - ((R**2)*(r + R**2)**2*(-d**2 + 4*r**2 + 8*r*R**2 + 4*R**4))**(1/2)/(2*(r + R**2)**2)
        
    #convert to mm
    x = x*1000

    #calculate movement in theta axis based on xtslope, the linear relationship
    #between the movement in the theta-axis and r-axis
    theta = xtslope*x
    
    print("movement in r-axis (mm) = ", x)
    print("movement in theta-axis(deg) = ",theta)
    
    
    #calculate the steps for r-axis movement
    spr_r = 4 * R_gear_num  # steps per revolution
    steps_r = x/ballscrew_lead*spr_r*radius_gear_ratio
    send_steps_r = int(round(steps_r))

    #test output for r-axis
    print("steps = ", steps_r)
    print("steps int = ", int(round(steps_r)))
    
    
    #calculate the steps for theta-axis movement
    spr_t = 4 * T_gear_num  # steps per revolution for theta-axis servo
    steps_t = spr_t * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps_t = int(round(steps_t))

    #test output for theta-axis
    print("steps = ", steps_t)
    print("steps int = ", int(round(steps_t)))
    

    #send the steps for r-axis and t-axis to the drives
    Send(radius_drive_id,Go_Relative_Pos,send_steps_r)
    Send(angle_drive_id,Go_Relative_Pos,send_steps_t)
    

    #test code to test servo drive max acceleration and velocity constants
    #z = 1000000
    #Send(radius_drive_id,Go_Relative_Pos,z)
    #Send(angle_drive_id,Go_Relative_Pos,int(z*0.38119333))
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Moving To Curving Position, Radius of Curvature: " + str(radius_curvature) + " m"
    
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

    clear()     #comment out when debugging so the screen doesn't get cleared
    
    print("----------------------------------------------------")
    print("ADVANCED TECHNOLOGY STRUCTURES PVC PROFILE ASSEMBLER")
    print("----------------------------------------------------\n")

    
    print("Linear Speed (of profile) Set Point\t",linear_speed,"m/min")
    print("STAGE 1 RPM Set Point\t\t\t",get_rpm(linear_speed,roller_diameter,stage1_gear_ratio),"rpm")
    print("STAGE 2 RPM Set Point\t\t\t",get_rpm(linear_speed,roller_diameter,stage2_gear_ratio),"rpm")
    print("\n")
    
    print("Stage 1 Maximum Acceleration\t\t",max_motor_acceleration(k_stage1_mAcc,gear_ratio(stage1_gear_num)),"rpm/s")
    print("Stage 1 Maximum Speed\t\t\t",max_motor_speed(k_stage1_mSpeed,gear_ratio(stage1_gear_num)),"rpm")
    print("\n")
    
    print("Stage 2 Maximum Acceleration\t\t",max_motor_acceleration(k_stage2_mAcc,gear_ratio(stage2_gear_num)),"rpm/s")
    print("Stage 2 Maximum Speed\t\t\t",max_motor_speed(k_stage2_mSpeed,gear_ratio(stage2_gear_num)),"rpm")
    print("\n")
    
    print("R-axis Maximum Acceleration\t\t",max_motor_acceleration(k_radius_mAcc,gear_ratio(R_gear_num)),"rpm/s")
    print("R-axis Maximum Speed\t\t\t",max_motor_speed(k_radius_mSpeed,gear_ratio(R_gear_num)),"rpm")
    print("R-axis High Speed Constant\t\t",k_radius_mSpeed,"[Unitless]")
    print("R-axis High Acceleration Constant\t",k_radius_mAcc,"[Unitless]")
    print("\n")
    
    print("T-axis Maximum Acceleration\t\t",max_motor_acceleration(k_theta_mAcc,gear_ratio(T_gear_num)),"rpm/s")
    print("T-axis Maximum Speed\t\t\t",max_motor_speed(k_theta_mSpeed,gear_ratio(T_gear_num)),"rpm")
    print("T-axis High Speed Constant\t\t",k_theta_mSpeed,"[Unitless]")
    print("T-axis High Acceleration Constant\t",k_theta_mAcc,"[Unitless]")
    print("\n")
    print("Last Action:",last_action)
    print("\n")
    print("Command Options")

    for i in range(0, len(menu_items)):
        print(i, "-", menu_items[str(i)][1])

    print("x - exits the program")

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

#uncomment me to run on pi
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
#print(ToController)
#for a in ToController:
#    print(binary_display_int(a))

#read 100 characters and store it in str msg
print("Data Received:")
msg = ser.read(1000)                    #uncomment me to run on pi

#print the string msg
print(msg)                              #uncomment me to run on pi
print("\n")

# End of Send code ---------------------------------------------------------

time.sleep(5)

# Main Program [START] -----------------------------------------------------

while True:

    hmi_display(menu_items)

    command = input("Input Command:")

    if command == "x" or command == "exit":
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
#typically the data that is received is 7 bytes in a packet.
#B6 B5 B4 B3 B2 B1 B0
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

#2018-08-29 
#do not use send the make linear line function to the servo. It is not supported by DMM.
#max acceleration r = 16
#max acceleration theta = 6
#max velocity r = 33
#max velocity theta = 19