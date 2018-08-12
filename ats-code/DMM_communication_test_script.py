# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 18:19:52 2018

@author: Owner
"""

import DMM_Servo_Communication as com
import time as t

stage1_drive_id = 10 # drive id for stage 1 servo drive that runs the stage 1 set of rollers
stage2_drive_id = 20 # drive id for stage 2 servo drive that runs the stage 2 set of rollers
radius_drive_id = 21 # drive id for the servo drive that controls the stage 2 platform that changes the bend radius of the machine
angle_drive_id = 22 # drive id for the servo drive that controls the angle of the entire stage 2 platform.
dummy = 0x83

#maybe read alarms into rasspi
com.InitializeCommunication() 
com.Send(stage1_drive_id, com.Set_Origin, dummy) #set current position to zero
print('Current position set to zero')

com.Send(stage1_drive_id, com.Go_Absolute_Pos, 10000) #unclear on how to read position of servo maybe ask DMM
print('should move to position 10000 and stop, 10 seconds should eclipse since start of move before next one')
t.sleep(10)

com.Send(stage1_drive_id, com.Go_Absolute_Pos, -10000) #unclear on how to read position of servo maybe ask DMM
print('should move to position -10000 and stop, 10 seconds should eclipse since start of move before next one')
t.sleep(10)

# once the bugs are worked out of this build it into a function 
# ex gain = GetGain(ID) have internal statement that prints error if unable to get answer
var = (False, 'asdf', 'asdf', 'asdf')
while var[0] == False:
    com.Send(stage1_drive_id, com.Read_MainGain, dummy)
    var = com.Obtain()
Gain = var[3]
print('getting gain')
print('gain is ', Gain)

print('changing gain to value 70')
com.Send(stage1_drive_id, com.Set_MainGain, 70)

print('checking if gain was changed')
var = (False, 'asdf', 'asdf', 'asdf')
while var[0] == False:
    com.Send(stage1_drive_id, com.Read_MainGain, dummy)
    var = com.Obtain()
Gain2 = var[3]
print('new gain is', Gain2)

print('reseting gain to original value')
com.Send(stage1_drive_id, com.Set_MainGain, Gain)

print('checking if gain was changed')
var = (False, 'asdf', 'asdf', 'asdf')
while var[0] == False:
    com.Send(stage1_drive_id, com.Read_MainGain, dummy)
    var = com.Obtain()
Gain3 = var[3]
print('new gain is', Gain3)


