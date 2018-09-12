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




# Drive ID's
stage1_drive_id = 10 # drive id for stage 1 servo drive that runs the stage 1 set of rollers
stage2_drive_id = 20 # drive id for stage 2 servo drive that runs the stage 2 set of rollers
radius_drive_id = 21 # drive id for the servo drive that controls the stage 2 platform that changes the bend radius of the machine
angle_drive_id = 22 # drive id for the servo drive that controls the angle of the entire stage 2 platform.
# the servo driven by this servo drive is attached to the rack and pinion on stage 2 of the machine
general_drive_id = 127

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

print("part 1 initialization done")

# MACHINE CHARACTERISTICS ---------------------------- [END]

# INITIALIZATION ---------------------------- [START]

#BRAD'S code for initializing servos
taxis = com.Position(angle_drive_id)
print("taxis")
raxis = com.Position(radius_drive_id)
print("raxis")
stage1 = com.Position(stage1_drive_id)
print("stage 1")
stage2 = com.Position(stage2_drive_id)
print("stage2")
print("objects initialized")

raxis.sethighspeed(40)
raxis.sethighacl(16)
taxis.sethighspeed(12)
taxis.sethighacl(6)
print("speed and accel set")

#define variable for linear speed in m/min.
#default value is 1.0 m/min
linear_speed = 1.0 #m/min
radius_curvature = 1.5 #15.240 #m

for i in range(0,5):
    raxis.GearNum = 4096 #gear_num parameter for the r-axis servo
    taxis.GearNum = 4096 #gear_num parameter for the theta-axis servo
    stage1.GearNum = 4096 #gear_num parameter for the stage 1 servo
    stage2.GearNum = 4096 #gear_num parameter for the stage 2 servo
print("gearnums set")
#gear number is from 500 to 16384

#default values for max speed and max acceleration
#valid values are between 1 and 127 (integer)
#these values should be read in in the initalization period once we have the read functionality working
#stage1.MaxAcceleration = 2
#stage2.MaxAcceleration = 2

stage1.HighAccel = 30
stage2.HighAccel = 30
k_radius_mAcc = raxis.HighAccel
k_theta_mAcc = taxis.HighAccel

k_stage1_mSpeed = 50
k_stage2_mSpeed = 50
k_radius_mSpeed = raxis.HighSpeed
k_theta_mSpeed = taxis.HighSpeed
print("objects fully set")

last_action = "N/A"

# INITIALIZATION ---------------------------- [END]


# High Level Functions [Start] -------------------------------------------------------


def get_rpm(speed,servo):
    '''
    :param speed: desired linear speed in m/min that machine will process profiles
    :param servo: servo to calculate for
    '''
    
    rpm = servo.GearNum*speed*1000/(3.14159*roller_diameter*25.4)
    #print("Linear Speed is",s,"m/min")
    #print("RPM of motor is",round(rpm),"rpm")

    return int(rpm)

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
         "1":[1,"Start Stage 1 Rollers",stage1_start,get_rpm(linear_speed,stage1)],
         "2":[2,"Start Stage 2 Rollers",stage2_start,get_rpm(linear_speed,stage2)],
         "3":[3,"Set Linear Speed (m/min)",set_linear_speed],
         "4":[4,"Set Radius of Curvature (m)",set_radius],
         "5":[5,"Move R-Axis (mm)",move_Raxis],
         "6":[6,"Move Theta-Axis (deg)",move_Taxis],
         "7":[7,"Move to Curving Position",move_Curve],
         "8":[8,"Zero curving position",zero],
         "9":[9,"Move curve to zero (home) position",home]
         }
    return a

def home():
    raxis.AbsPos = 0
    taxis.AbsPos = 0
    
    global last_action
    last_action = "Curve is moved back to zero (home) position"    
    return 

def zero():
    '''
    :sets the raxis and thetaxis to a zero or origin point
    '''
    raxis.SetOrigin()
    taxis.SetOrigin()
    
    global last_action
    last_action = "radius and theta axes set to zero at current position"    
    return   

    #for later on when we incorporate a proximity sensor
    #com.ConstSpeed(raxis.driveID,60) #move servo closer to the sensor
    #com.ConstSpeed(thetaxis.driveID,60)
    #while (radlimit == false):
        #test GPIO to determine when radlimit becomes true
    #com.ConstSpeed(raxis.driveID,0)
    #com.ConstSpeed(thetaxis.driveID,0)
    #raxis.SetOrigin()
    #thetaxis.SetOrigin()

def stage1_start(rpm):
    '''
    :param rpm:
    :return:
    '''
    for i in range(0,5):
        com.ConstSpeed(stage1.driveID, rpm)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Stage 1 Started at " + str(rpm) + " rpm"
    
    return

def stage2_start(rpm):
    '''
    :param rpm:
    :return:
    '''
    
    for i in range(0,5):
        com.ConstSpeed(stage2.driveID, rpm)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Stage 2 Started at " + str(rpm) + " rpm"
    
    return

def stop_all():
    '''

    :return:
    '''

    taxis.Stop()
    raxis.Stop()
    stage1.Stop()
    stage2.Stop()
    
    com.ConstSpeed(taxis.driveID,0)
    com.ConstSpeed(raxis.driveID,0)
    com.ConstSpeed(stage1.driveID,0)
    com.ConstSpeed(stage2.driveID,0)
    
    #Send(stage1_drive_id,Turn_ConstSpeed,0)
    #Send(stage2_drive_id,Turn_ConstSpeed,0)
    #Send(radius_drive_id,Turn_ConstSpeed,0)
    #Send(angle_drive_id,Turn_ConstSpeed,0)
    
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
    spr = 4 * raxis.GearNum #R_gear_num  # steps per revolution
    print(spr)
    steps = d/ballscrew_lead*spr*radius_gear_ratio
    send_steps = int(round(steps))

    print(steps)
    print(int(round(steps)))

    raxis.AbsPos = send_steps
    #raxis.GoToRel(send_steps)
    #Send(radius_drive_id,Go_Relative_Pos,send_steps)
    
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
    spr = 4 * taxis.GearNum #T_gear_num  # steps per revolution for theta-axis servo
    print(spr)
    steps = spr * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps = int(round(steps))

    print(steps)
    print(int(round(steps)))

    taxis.AbsPos = send_steps
    #taxis.GoToRel(send_steps)
    #Send(angle_drive_id,Go_Relative_Pos,send_steps)

    # how many steps in a full revolution???
    # n = steps in a full revolution
    # n = 16384/Gear_Ratio or n = 4*Gear_Num
    
    #set last_action message on hmi screen
    global last_action
    last_action = "T-axis moved by: " + str(theta) + " degrees, " + str(send_steps/spr) + " servo revs, " + str(send_steps) + " steps"

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
    spr_r = 4 * raxis.GearNum #R_gear_num  # steps per revolution
    print(spr_r)
    steps_r = x/ballscrew_lead*spr_r*radius_gear_ratio
    send_steps_r = int(round(steps_r))

    #test output for r-axis
    print("steps = ", steps_r)
    print("steps int = ", int(round(steps_r)))
    
    
    #calculate the steps for theta-axis movement
    spr_t = 4 * taxis.GearNum #T_gear_num  # steps per revolution for theta-axis servo
    print(spr_t)
    steps_t = spr_t * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps_t = int(round(steps_t))

    #test output for theta-axis
    print("steps = ", steps_t)
    print("steps int = ", int(round(steps_t)))
    

    #send the steps for r-axis and t-axis to the drives
    #Send(radius_drive_id,Go_Relative_Pos,send_steps_r)
    #Send(angle_drive_id,Go_Relative_Pos,send_steps_t)
    
    #send the steps for r-axis and t-axis to the drives
    Send(radius_drive_id,Go_Absolute_Pos,send_steps_r)
    Send(angle_drive_id,Go_Absolute_Pos,send_steps_t
    
    
    
    #taxis.GoToRel(send_steps_r)
    #raxis.GoToRel(send_steps_t)

    taxis.AbsPos = send_steps_r
    raxis.AbsPos = send_steps_t

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
    print("STAGE 1 RPM Set Point\t\t\t",get_rpm(linear_speed,stage1),"rpm")
    print("STAGE 2 RPM Set Point\t\t\t",get_rpm(linear_speed,stage2),"rpm")
    print("\n")
    
    #print("Stage 1 Maximum Acceleration\t\t",max_motor_acceleration(k_stage1_mAcc,gear_ratio(stage1_gear_num)),"rpm/s")
    #print("Stage 1 Maximum Speed\t\t\t",max_motor_speed(k_stage1_mSpeed,gear_ratio(stage1_gear_num)),"rpm")
    #print("\n")
    print("Stage 1 Maximum Acceleration\t\t",stage1.MaxAcceleration,"rpm/s")
    print("Stage 1 Maximum Speed\t\t\t",stage1.MaxSpeed,"rpm")
    print("\n")
    
    #print("Stage 2 Maximum Acceleration\t\t",max_motor_acceleration(k_stage2_mAcc,gear_ratio(stage2_gear_num)),"rpm/s")
    #print("Stage 2 Maximum Speed\t\t\t",max_motor_speed(k_stage2_mSpeed,gear_ratio(stage2_gear_num)),"rpm")
    #print("\n")
    print("Stage 2 Maximum Acceleration\t\t",stage2.MaxAcceleration,"rpm/s")
    print("Stage 2 Maximum Speed\t\t\t",stage2.MaxSpeed,"rpm")
    print("\n")
    
    #print("R-axis Maximum Acceleration\t\t",max_motor_acceleration(k_radius_mAcc,gear_ratio(R_gear_num)),"rpm/s")
    #print("R-axis Maximum Speed\t\t\t",max_motor_speed(k_radius_mSpeed,gear_ratio(R_gear_num)),"rpm")
    print("R-axis Maximum Acceleration\t\t",raxis.MaxAcceleration,"rpm/s")
    print("R-axis Maximum Speed\t\t\t",raxis.MaxSpeed,"rpm")
    print("R-axis High Speed Constant\t\t",k_radius_mSpeed,"[Unitless]")
    print("R-axis High Acceleration Constant\t",k_radius_mAcc,"[Unitless]")
    print("\n")
    
    #print("T-axis Maximum Acceleration\t\t",max_motor_acceleration(k_theta_mAcc,gear_ratio(T_gear_num)),"rpm/s")
    #print("T-axis Maximum Speed\t\t\t",max_motor_speed(k_theta_mSpeed,gear_ratio(T_gear_num)),"rpm")
    print("T-axis Maximum Acceleration\t\t",taxis.MaxAcceleration,"rpm/s")
    print("T-axis Maximum Speed\t\t\t",taxis.MaxSpeed,"rpm")
    print("T-axis High Speed Constant\t\t",k_theta_mSpeed,"[Unitless]")
    print("T-axis High Acceleration Constant\t",k_theta_mAcc,"[Unitless]")
    print("\n")
    print("Current Radius of curvature\t",radius_curvature,"  m or ft")
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
#ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)  #this is the only serial port we use on the pi


#ser.baudrate = 38400
#ser.timeout = 2
#ser.PARITY_NONE
#ser.STOPBITS_ONE
#ser.EIGHTBITS

#PACKET DEFINITION
#DRIVE ID, FUNCTION CODE, AND DATA
#set the varibles below to set the data that will be sent.
driveID = general_drive_id
#FunctionCode = Read_FoldNumber #packet function code see page 53. Function Code
data = 1 #data to be sent. Data can be max speed, gear number, etc.

#ToController = Send(driveID, FunctionCode, data)
#everything works, packets are sent properly, negative numbers may need to 
#be properly formatted

#Sends Binary output to console for debugging purposes
#print(ToController)
#for a in ToController:
#    print(binary_display_int(a))

#read 100 characters and store it in str msg
print("Data Received:")
#msg = ser.read(1000)                    #uncomment me to run on pi

#print the string msg
#print(msg)                              #uncomment me to run on pi
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