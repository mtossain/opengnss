#!/usr/bin/env python

from numpy import *
import pylab as p


fs = 2e6
N = 2**11
t = arange( 0.0, 20*N/fs, 1.0/fs )
m = N/fs

# Taken from tsui.
threshold = 2*pi/5


def truncate(x, N):
    foo = len(x) % N
    if foo > 0:
        return x[:-foo]
    else:
        return x


def dft(x, f):
    kernel = e**( -2j*pi*f*t )
    kernel = truncate( kernel, N )
    kernel = reshape( kernel, (-1, N))
    
    return array( [ sum( x[n] * kernel[n] ) for n in range(20) ] )


# Generate input signal.
f = 1.34312341e3
x = truncate( 1.0*e**(2j*pi*f*t), N )
x = x + 0.01*random.randn(len(x))
x = reshape( x, (-1, N))


# Coarse resolution acquisition
f_coarse = abs(fft.fft(x[0])).argmax()/m


# Medium resolution calculation.
f_medium = array( [f_coarse-400, f_coarse, f_coarse+400] )
Xk = array( [ abs(dft(x,f_i)[0]) for f_i in f_medium ] )
f_medium = f_medium[ Xk.argmax() ]


# Fine frequency calculation.
Xk = dft(x, f_medium)
theta = angle(Xk)
d_theta = array([ theta[n] - theta[n-1] for n in range(1, len(theta)) ])
d_theta = array(map( lambda x: ((abs(x) > threshold) and (x-2*pi)) or x, d_theta))
f_fine = f_medium + sum(d_theta)*fs/(len(d_theta)*N*pi*2)


print """OpenGNSS fine frequency estimation."""

print """
True frequency:                         %f Hz
Coarse resolution calculation result:   %f Hz
Medium resolution calculation result:   %f Hz
Fine frequency calculation result:      %f Hz""" % (f, f_coarse, f_medium, f_fine)



