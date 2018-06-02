import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14,GPIO.OUT)
print("LED on")
GPIO.output(14,GPIO.HIGH)
time.sleep(1)
print("LED off")
GPIO.output(14,GPIO.LOW)

import serial
ser = serial.Serial('/dev/ttyAMA0')
print(ser.name)
ser.baudrate = 1
print(ser.baudrate)

ser.write('~')
ser.close()
