# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 07:22:05 2018

@author: henra
"""
import time
import sys
import serial
from RPi import GPIO

# initialize the pi's serial port to controller parameters
# page 50 of controller manual
ser = serial.Serial("/dev/serial0")  #this is the only serial port we use on the pi
ser.baudrate = 38400
ser.timeout = 2
ser.PARITY_NONE
ser.STOPBITS_ONE
ser.EIGHTBITS






def checkopen(port):
    if port.is_open == True:
        print("Connection is open")
    elif port.is_open == False:
        print("Connection is closed")