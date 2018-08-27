import DMM_Servo_Communication as com
import math
import numpy
import os
# MACHINE CHARACTERISTICS ---------------------------- [START]

# Drive ID's
stage1_drive_id = 10 # drive id for stage 1 servo drive that runs the stage 1 set of rollers
stage2_drive_id = 20 # drive id for stage 2 servo drive that runs the stage 2 set of rollers
radius_drive_id = 21 # drive id for the servo drive that controls the stage 2 platform that changes the bend radius of the machine
angle_drive_id = 22 # drive id for the servo drive that controls the angle of the entire stage 2 platform.
# the servo driven by this servo drive is attached to the rack and pinion on stage 2 of the machine
general_drive_id = 127
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




# INITIALIZATION ---------------------------- [START]

#define variable for linear speed in m/min.
#default value is 1.0 m/min
linear_speed = 1.0
gear_num = 4096

#default values for max speed and max acceleration
#valid values are between 1 and 127 (integer)
#these values should be read in in the initalization period once we have the read functionality working
k_stage1_mAcc = 2
k_stage2_mAcc = 2
k_radius_mAcc = 2
k_theta_mAcc = 2

k_stage1_mSpeed = 50
k_stage2_mSpeed = 50
k_radius_mSpeed = 50
k_theta_mSpeed = 50



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
    a = input("Input linear process speed of profile (m/min) (+'ve for forward through the machine, -'ve for reverse):")
    linear_speed = float(a)
    print("linear_speed",linear_speed)
    menu_items = generate_menu_items()
    return

def generate_menu_items():
    a = {"0":[0,"Stop All Rollers",stop_all],
         "1":[1,"Start Stage 1 Rollers",stage1_start,get_rpm(linear_speed,roller_diameter,stage1_gear_ratio)],
         "2":[2,"Start Stage 2 Rollers",stage2_start,get_rpm(linear_speed,roller_diameter,stage2_gear_ratio)],
         "3":[3,"Set Linear Speed (m/min)",set_linear_speed],
         "4":[4,"Move R-Axis (mm)",move_Raxis]}
    return a

def stage1_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage1_drive_id,Turn_ConstSpeed,rpm)
    com.Send(general_drive_id, com.Turn_ConstSpeed, rpm)
    print("Stage 1 Started at",rpm,"rpm")
    return

def stage2_start(rpm):
    '''
    :param rpm:
    :return:
    '''

    #Send(stage2_drive_id,Turn_ConstSpeed,rpm)
    com.Send(general_drive_id, com.Turn_ConstSpeed, rpm)
    print("Stage 2 Started at",rpm,"rpm")
    return

def stop_all():
    '''
    :return:
    '''

    com.Send(stage1_drive_id,com.Turn_ConstSpeed,0)
    com.Send(stage2_drive_id,com.Turn_ConstSpeed,0)
    com.Send(radius_drive_id,com.Turn_ConstSpeed,0)
    com.Send(angle_drive_id,com.Turn_ConstSpeed,0)
    print("All drives stopped")
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
    spr = 4 * gear_num  # steps per revolution
    steps = d/ballscrew_lead*spr*radius_gear_ratio
    send_steps = int(round(steps))

    print(steps)
    print(int(round(steps)))

    #Send(radius_drive_id,Go_Relative_Pos,send_steps)
    com.Send(general_drive_id,com.Go_Relative_Pos,send_steps)

    # how many steps in a full revolution???
    # n = steps in a full revolution
    # n = 16384/Gear_Ratio or n = 4*Gear_Num

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
    print("R-axis Maximum Speed\t\t",max_motor_speed(k_radius_mSpeed,gear_ratio(gear_num)),"rpm")
    print("R-axis Maximum Acceleration\t",max_motor_acceleration(k_radius_mAcc,gear_ratio(gear_num)),"rpm/s")
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
FunctionCode = com.Read_FoldNumber #packet function code see page 53. Function Code
data = 1 #data to be sent. Data can be max speed, gear number, etc.

#test code
print("OutData")
print(com.OutData(16384))
a = int(numpy.binary_repr(16384,14)[0:7],2) + 0x80
b = int(numpy.binary_repr(16384,14)[7:14],2) + 0x80
c = int(numpy.binary_repr(16384,14)[14:21],2) + 0x80



ToController = com.Send(driveID, FunctionCode, data)
#everything works, packets are sent properly, negative numbers may need to 
#be properly formatted

#Sends Binary output to console for debugging purposes
print(ToController)
for a in ToController:
    print(com.binary_display_int(a))

#read 100 characters and store it in str msg
print("message read")
#msg = ser.read(1000)                    #uncomment me to run on pi

#print the string msg
#print(msg)                              #uncomment me to run on pi

# End of Send code ---------------------------------------------------------

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
