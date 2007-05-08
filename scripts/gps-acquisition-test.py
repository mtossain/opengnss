#!/usr/bin/env python

from numpy import *
from scipy import signal
import pylab as p
from gps import *


if __name__ == "__main__":
    if 1:
        fs = 4e6
        x = fromfile('data/L1-4MHz-svn1-nav.dat', dtype=complex64)
        # Drop the inital samples, they contain nasty spikes.
        x = x[8000:]
    elif 0:
        fs = 2e6
        x = fromfile('data/L1-2MHz-svn1.dat', dtype=complex64)
        # Drop the inital samples, they contain nasty spikes.
        x = x[4000:]
    else:
        fs = 4e6
        code = ca_code.ca_code(1, fs, ca_shift=123)
        code = r_[ code, -code, code, code, code, code ]
        f = array ( [ e**( 2j*pi*7.129812735062512e3*n/fs) for n in arange(len(code)) ] )
#         f = f + 3*random.randn(len(f))
        x = code * f


    acq = Acquisition(fs=fs, svn=1)
    (fd, ca_delay) = acq.calc(x)
    print "Doppler frequency: %f" % fd
    print "C/A delay: %d" % ca_delay

    # filters
    a = [1.0]
    b_code = signal.firwin( 60, 20e3/fs )
    b_doppler = signal.firwin( 60, 10/fs ) 

    x = reshape(x, (-1, 1e-3*fs))
    x = x[:10]


    # C/A Code removed
    code = ca_code(1, fs, ca_shift=(ca_delay))
    m = signal.lfilter( b_code, a, code * x )

    # With Doppler.
#     p.figure()
#     p.subplot(211)
#     M = abs(fft.fft(m.ravel()))
#     p.plot( r_[ M[len(M)/2:], M[:len(M)/2] ] )
#     p.subplot(212)
#     m = signal.lfilter( b, a, m )
#     M = abs(fft.fft(m.ravel()))
#     p.plot( r_[ M[len(M)/2:], M[:len(M)/2] ] )


    # Mix down to baseband.
    f = array ( [ e**( -2j*pi*(fd)*n/fs) for n in arange(m.size) ])
    f.shape = m.shape
    m = f * m
#     m = signal.lfilter( b_doppler, a, m )


    # Without Doppler.
    p.figure()
    p.subplot(2,1,1)
    p.plot(m.ravel())
    p.subplot(2,1,2)
    M = abs(fft.fft(m.ravel()))
    p.plot( r_[ M[len(M)/2:], M[:len(M)/2] ] )

    p.figure()
    p.plot(signal.resample(m.ravel(), 200))
    p.show()

# vim: ai ts=4 sts=4 et sw=4
