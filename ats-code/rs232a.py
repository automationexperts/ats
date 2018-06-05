import time
import sys
import serial
from RPi import GPIO

#BACKGROUND INFO
#   for this script to work the Rx and Tx pins on the raspberry pi must be
#   connected to one another. This is also known as an RS232 Loopback test

def checkopen():
    if ser.is_open == True:
        print("Connection is open")
    elif ser.is_open == False:
        print("Connection is closed")
    pass

#CONNECTION SETUP
print(sys.version)
#ser = serial.Serial("/dev/ttyAMA0", baudrate =  38400, timeout = 1000)
#note that /dev/serial0 brings up the default serial port whereas ttyAMA0
#attempts to access the UART used for the bluetooth on the raspberry pi 3
ser = serial.Serial("/dev/serial0", baudrate =  38400, timeout = 2)
print(ser.name)
print("Baudrate = {b}".format(b=ser.baudrate))

#CAN USE THIS FOR SETTING BAUDRATE AFTER CONNECTION IS SETUP
#ser.baudrate = 38400
#print("Baudrate = {b}".format(b=ser.baudrate))

#OPEN CONNECTION AND CHECK
checkopen()

#WRITE SOMETHING
ser.write(b"hello test")
ser.write("hello test")

#read one character
#msga = ser.read()

#read 100 characters and store it in str msg
msg = ser.read(100)

#print the string msg
print(msg)

#print the type of msg
print(type(msg))

#CLOSE CONNECTION AND CHECK
ser.close()
checkopen()
