# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 19:11:23 2018

@author: Owner
"""

import DMM_Servo_Communication as com

# Use DMMDRV software to set both servos as position servos

#modify the X and Y to be proper drive ID's
ID_X = 5 # drive ID of x axis
ID_Y = 6 # drive ID of y axis
ID_Z = 7 # fake drive ID of z axis
General_ID = 127 # general drive ID used to address all drives

Make_LinearLine = 0x02  #function code for linear line

com.Send(ID_X, Make_LinearLine, 100)
com.Send(ID_Y, Make_LinearLine, 100)
com.Send(ID_Z, Make_LinearLine, 100) #z is fake
com.Send(General_ID, Make_LinearLine, 5) #feedrate

