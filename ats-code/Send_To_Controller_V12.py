# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 07:46:38 2018

@author: Owner
"""

import time
import numpy
import os
import DMM_Servo_Communication as com

# MACHINE CHARACTERISTICS ----------------------------

#gearbox ratios
stage1_gear_ratio = 60 #gear ratio for gearbox that drives stage 1 rollers
stage2_gear_ratio = 60 #gear ratio for gearbox that drives stage 2 rollers
radius_gear_ratio = 40 #gear ratio for gearbox that drives stage 2 sled that adjusts the bend radius
theta_gear_ratio = 32 #gear ratio for the gearbox that adjusts the angle of stage 2

#define roller diameter in inches
roller_diameter = 10.0
roller_radius = roller_diameter/2*25.4/1000 

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

# Servo parameters and iniitialization
thetaxis = com.Position(22)
raxis = com.Position(21)
stage1 = com.Position(10)
stage2 = com.Position(20)

thetaxis.GearNum = 4096 #gear_num parameter for the theta-axis servo
raxis.GearNum = 4096 #gear_num parameter for the r-axis servo
thetaxis.HighAccel = 2
raxis.HighAccel = 2
thetaxis.HighSpeed = 50
raxis.HighSpeed = 50

# higher level functions

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
         "1":[1,"Start Stage 1 Rollers",stage1_start,get_rpm(linear_speed,roller_diameter,stage1_gear_ratio)],
         "2":[2,"Start Stage 2 Rollers",stage2_start,get_rpm(linear_speed,roller_diameter,stage2_gear_ratio)],
         "3":[3,"Set Linear Speed (m/min)",set_linear_speed],
         "4":[4,"Set Radius of Curvature (m)",set_radius],
         "5":[5,"Move R-Axis (mm)",move_Raxis],
         "6":[6,"Move Theta-Axis (deg)",move_Taxis],
         "7":[7,"Move to Curving Position",move_Curve]
         "8":[8,"Zero curving position",zero],
         }
    return a

def zero():
    '''
    :sets the raxis and thetaxis to a zero or origin point
    '''
    raxis.SetOrigin()
    thetaxis.SetOrigin()
    
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

    com.ConstSpeed(stage2.driveID, rpm)
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Stage 2 Started at " + str(rpm) + " rpm"
    
    return

def stop_all():
    '''

    :return:
    '''

    stage1.Stop()
    stage2.Stop()
    thetaxis.Stop()
    raxis.Stop()
    
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
    spr = 4 * raxis.GearNum  # steps per revolution
    steps = d/ballscrew_lead*spr*radius_gear_ratio
    send_steps = int(steps)

    print(steps)
    print(int(steps))

    com.GoRelativePosition(raxis.driveID, steps)
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
    spr = 4 * thetaxis.GearNum  # steps per revolution for theta-axis servo
    steps = spr * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps = int(steps)

    print(steps)
    print(int(round(steps)))

    com.GoRelativePosition(thetaxis.driveID, steps)

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
    spr_r = 4 * raxis.GearNum  # steps per revolution
    steps_r = x/ballscrew_lead*spr_r*radius_gear_ratio
    send_steps_r = int(steps_r)

    #test output for r-axis
    print("steps = ", steps_r)
    print("steps int = ", int(steps_r))
    
    
    #calculate the steps for theta-axis movement
    spr_t = 4 * thetaxis.GearNum  # steps per revolution for theta-axis servo
    steps_t = spr_t * (n_rack/n_pinion) * theta / 360 * theta_gear_ratio #use formula to calculate steps made by the servo
    send_steps_t = int(steps_t)

    #test output for theta-axis
    print("steps = ", steps_t)
    print("steps int = ", int(steps_t))

    #send the steps for r-axis and t-axis to the drives
    raxis.AbsPos = send_steps_r
    thetaxis.AbsPos = send_steps_t
    
    #com.Go_Relative_Pos(raxis.driveID,send_steps_r)
    #com.Go_Relative_Pos(thetaxis.driveID,send_steps_t)

    #test code to test servo drive max acceleration and velocity constants
    #z = 1000000
    #Send(radius_drive_id,Go_Relative_Pos,z)
    #Send(angle_drive_id,Go_Relative_P#os,int(z*0.38119333))
    
    #set last_action message on hmi screen
    global last_action
    last_action = "Moving To Curving Position, Radius of Curvature: " + str(radius_curvature) + " m"
    
    return

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
    
    print("Stage 1 Maximum Acceleration\t\t",stage1.MaxAcceleration,"rpm/s")
    print("Stage 1 Maximum Speed\t\t\t",stage1.MaxSpeed,"rpm")
    print("\n")
    
    print("Stage 2 Maximum Acceleration\t\t",stage2.MaxAcceleration,"rpm/s")
    print("Stage 2 Maximum Speed\t\t\t",stage2.MaxSpeed,"rpm")
    print("\n")
    
    print("R-axis Maximum Acceleration\t\t",raxis.MaxAcceleration,"rpm/s")
    print("R-axis Maximum Speed\t\t\t",raxis.MaxSpeed,"rpm")
    print("\n")
    
    print("T-axis Maximum Acceleration\t\t",thetaxis.MaxAcceleration,"rpm/s")
    print("T-axis Maximum Speed\t\t\t",thetaxis.MaxSpeed,"rpm")
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



# Operating System Functions [End]
    
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