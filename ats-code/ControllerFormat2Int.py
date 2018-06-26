# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 13:52:12 2018

@author: henra
"""

def ControllerFormat2Int(data):
    #Converts the data part of input from controller to properly formatted 
    #integer, takes care of 2's complement notation also 
    Length = len(data)
    num = 0
    for i in range(Length-2,1,-1): 
        placeMover = 2 ** ((Length-2-i) * 7) #multiplier to put integer in proper place
        num = num +int(bin(data[i])[3:],2) * placeMover
    # previous for loop formats integer num approprately from incoming data need to still apply 2's complement
    if ((Length-3) == 1) and (num > 63):
        num = num - 128
    if ((Length-3) == 2) and (num > 8191):    
        num = num - 16384
    if ((Length-3) == 3) and (num > 1048575):    
        num = num - 2097152
    if ((Length-3) == 4) and (num > 134217727):    
        num = num - 268435456   
    return num