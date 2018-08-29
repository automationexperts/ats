# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 16:26:34 2018

@author: Owner
"""

#test script for position servo objects
import DMM_Servo_Communication as com
com.InitializeCommunication()

driveA = 21
driveB = 22

drive21 = com.Position(21)
drive22 = com.Position(22)

print(drive21.MainGain)
print(drive22.MainGain)
