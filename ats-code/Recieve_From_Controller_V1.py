# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 11:02:23 2018

@author: henra
"""

def ErrorCheck(line): #uses the last bit recieved to check for errors in transmission pg 55
    # Returns True if there is an error, False if not
    length = len(line)
    endbit = int(bin(msg[length-1])[2:10],2) - 0x80
    total = 0
    for i in range(0,length-1):
        total = int(bin(msg[i])[2:10],2) + total
    temp = total % 128
    print(temp)
    print(endbit)
    if temp == endbit: #no error detected
        x = False
        return x
    else:
        x = True
        return x
    
    

# assume that ser is the serial object we are using
# be sure we have a timeout set, maybe 1 or 2 seconds
# msg = ser.read(100)
msg = b'\x15\xba\xa9\xb5\xad' #dummy variable for use when not connected to pi

# interpret information recieved from servo controller
ControllerID = msg[0]
packetLength = int(bin(msg[1])[3:5],2) + 4
purpose = int(bin(msg[1])[5:10],2)
data = list()
for i in range(2,packetLength-1):
    data.append(int(bin(msg[i])[3:10],2))
print(ErrorCheck(msg))



