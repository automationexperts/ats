# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 19:11:23 2018

@author: Owner
"""

import DMM_Servo_Communication as com

# Use DMMDRV software to set both servos as position servos

#modify the X and Y to be proper drive ID's
ID_X = 21 # drive ID of x axis
ID_Y = 22 # drive ID of y axis
ID_Z = 7 # fake drive ID of z axis
General_ID = 127 # general drive ID used to address all drives

Make_LinearLine = 0x02  #function code for linear line
Make_CircularArc = 0x04

com.InitializeCommunication()

com.Send(ID_X, Make_LinearLine, 5000)
com.Send(ID_Y, Make_LinearLine, 10000)
com.Send(ID_Z, Make_LinearLine, 100) #z is fake
com.Send(General_ID, Make_LinearLine, 50) #feedrate

#com.Send(ID_X, Make_CircularArc, -100)
#com.Send(ID_Y, Make_CircularArc, 0)
#com.Send(ID_Z, Make_CircularArc, 0)
#com.Send(ID_X, Make_CircularArc, 100)
#com.Send(ID_Y, Make_CircularArc, 0)
#com.Send(ID_Z, Make_CircularArc, 0)
#com.Send(General_ID, Make_CircularArc,4) #may also be a negative 2 byte data bit to do CCW directions.