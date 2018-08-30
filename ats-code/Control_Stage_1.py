# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:34:59 2018

@author: Owner
"""

#set GPIO pins on pi to interface with arduino
#assumes direct connection, to boost power to 5V use one of the tricks from 3V tips and tricks
#if using MOSFET to change voltage note that a single element will invert signal, this can be fixed in software by
#flipping the 1 and 0 in the output function. Since the arduino is using a pullup resistor do not change the values there.

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
GPIO.output(12, 1)

#to start stage 1 rollers
GPIO.output(12, 0)

#to stop stage 1 rollers
GPIO.output(12, 1)