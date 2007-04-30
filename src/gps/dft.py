#!/usr/bin/env python

from numpy import *

class DFT:
    """Discrete Fourier Transform where the phase of the kernel function is
    continous between each calculation."""

    def __init__(self, fs, initial_phase=0):
        self.fs = fs
        self.initial_theta = initial_phase
        self.current_theta = self.initial_theta
        self.kernel = lambda f, theta, n: e**(-2j*pi*f*n/fs + 1j*theta)


    def calc(self, x, f):
        if x.ndim < 2:
            x = reshape(x, (1,-1))

        kernel = self.kernel(f, self.current_theta, arange(len(x)+1))
        # Update theta to ensure contieous phase.
        self.current_theta = angle( kernel[-1] )

        return sum( x * kernel[:1], axis=1 )


    def reset_theta(self):
        self.current_theta = self.initial_theta


# Simple test.
if __name__ == "__main__":
    import pylab as p

    fs = 10e3
    f = 0.3e3
    x = arange(1024)

    mydft = DFT(fs)

    k = array([ mydft.calc(x, f+i*400) for i in range(3)])

    start = 924
    stop = 1124

    for i in range(2):
        p.subplot(2,1,i+1)
        p.plot(k.ravel()[start+i*len(x):stop+i*len(x)])

    p.show()

# vim: ai ts=4 sts=4 et sw=4
