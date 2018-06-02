import sys
from RPi import GPIO
from time import sleep

#display the version of python being used.
print (sys.version)

#pins refer to the pins on the encoder
pin1 = 4
pin2 = 17
pin4 = 27
pin8 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin1, GPIO.IN)
GPIO.setup(pin2, GPIO.IN)
GPIO.setup(pin4, GPIO.IN)
GPIO.setup(pin8, GPIO.IN)

counter = 0

#hard-code lookup table for the mechanical encoder
encoderTable = {'0000':0.0, '1000':1.0, '0100':2.0, '1100':3.0, '0010':4.0, '1010':5.0, '0110':6.0, '1110':7.0, '0001':8.0, '1001':9.0, '0101':10.0, '1101':11.0, '0011':12.0, '1011':13.0, '0111':14.0, '1111':15.0}

#hard-code steps per revolution for the specific encoders we are using
encoderSteps = 16.0


#function for returning the angle of the encoder
def encoderAngle( table, binaryValue, steps ):
    #print(table.get(binaryValue))
    eAngle = 360/steps*table.get(binaryValue)
    print(eAngle)
    return
    

while counter == 0:
    #pin1LastState = GPIO.input(pin1)
    
    #input current state of each pin and store in their respective variables
    pin1State = GPIO.input(pin1)
    pin2State = GPIO.input(pin2)
    pin4State = GPIO.input(pin4)
    pin8State = GPIO.input(pin8)
    
    #create string for the combined state
    pinState = str(pin1State) + str(pin2State) + str(pin4State) + str(pin8State)
    #test what pinState looks like
    #print(pinState)

    #stops the loop when uncommented
    #counter = 1
    
    

    #call function that prints the angle of the encoder
    encoderAngle(encoderTable, pinState, encoderSteps)
    
    

#try:

#        while True:
#                pin1State = GPIO.input(pin1)
#                dtState = GPIO.input(dt)
#                if pin1State != pin1LastState:
#                        if dtState != clkState:
#                                counter += 1
#                        else:
#                                counter -= 1
#                        print counter
#               clkLastState = clkState
#                sleep(0.01)
#finally:
#        GPIO.cleanup()
