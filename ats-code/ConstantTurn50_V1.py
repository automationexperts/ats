# -*- coding: utf-8 -*-
"""
Created on Tue Jul  3 15:50:49 2018

@author: henra
"""
import serial

ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE)  #this is the only serial port we use on the pi

a=bytearray(b'\x15\x8a\xb2\xd1') # turn at 50 RPM constant speed

ser.write()
ser.flush()
ser.close()