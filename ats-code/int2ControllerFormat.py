# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 09:39:11 2018

@author: henra
"""

import numpy

#formats integers properly according to 2's complement rule
#see page 54
def int2ControllerFormat(num):
    #make sure 'import numpy' is at top of file
    if num > 0 and num < 64:
        output = int(numpy.binary_repr(num,7),2)
        return output
    if num > 63  and num < 8192:
        output = int(numpy.binary_repr(num,14),2)
        return output
    if num > 8191  and num < 1048576:
        output = int(numpy.binary_repr(num,21),2)
        return output
    if num > 1048575:
        output = int(numpy.binary_repr(num,28),2)
        return output
    if num > 134217727:
        print('error, input data out of range')
        return

    if num < 0 and num > -65:
        output = int(numpy.binary_repr(num,7),2)
        return output
    if num <-64  and num > -8193:
        output = int(numpy.binary_repr(num,14),2)
        return output
    if num <-8192  and num > -1048577:
        output = int(numpy.binary_repr(num,21),2)
        return output
    if num <-1048576:
        output = int(numpy.binary_repr(num,28),2)
        return output
    if num <-134217728:
        print('error, input data out of range')
        return