#!/usr/bin/env python
import numpy, scipy
from scipy import signal
import cmath

f_s = 5e3           # Sampling frequency.
t_s = 1.0/f_s       # Sampling period.
n = f_s*1e-3        # Number of samples in one milisecond.
f_c = 1.25e6        # L1 frequency without Doppler shift.

f_ca = 1.023e6      # Gold code frequency.
t_ca = 1.0/f_ca     # Gold code period.
n_ca = 1023         # Number of samples in C/A code.


def shift(data, n=1):
    """Shift the vector."""
    return numpy.concatenate( (data[-n:], data[:-n]) )


class CA:
    """CA code generator
    """
    def __init__(self, sv):
        self.code_delay_chips = [5,6,7,8,17,18,139,140,141,251,252,254,255,256,257,258,469,470,471,472,473,474,509,512,513,514,515,516,859,860,861,862]
        self.g1_generator = lambda reg: reg[2]*reg[9] 
        self.g2_generator = lambda reg: reg[1]*reg[2]*reg[5]*reg[7]*reg[8]*reg[9] 
        self.shift = self.code_delay_chips[sv]
        self.ca_code = -( self.__g_code(self.g1_generator) * shift(self.__g_code(self.g2_generator), self.shift))
        self.ca_code = signal.signaltools.resample(self.ca_code, 5000)
    
    def __g_code(self, code_function ):
        reg = -1*numpy.ones(10)
        g = numpy.empty(n_ca)

        for i in range(0,self.ca_length):
            g[i] = reg[9]
            save = code_function(reg)
            reg[1:10] = reg[0:9]
            reg[0] = save
        return g

    def get_code(self):
        """Returns the desired CA code."""
        return self.ca_code


class Acquisition:
    """Acquisition module.

    Locates the start of the C/A-code and course carrier frequency.
    """
    def __init__(self, sv):
        self.ca = CA(sv)
        self.__generate_local_codes()

    def __generate_local_codes(self):
        """Generates a matrix of all possible local codes."""
        ca = self.ca.get_code()

        # Generate time domain local codes.
        l_si = lambda df: [ ca[n]*cmath.exp(2j*cmath.pi*(f_c+df)*n) for n in range(0,5000) ]
        l_s = map( l_si, range(-10,11) )

        # Transform local codes to frequency domain.
        self.L_s = map(fft, l_s)

    def search(self, gps_signal):
        """Search through all code delay chips and doppler shifts."""

        X = fft(gsp_signal)
        R = map( lambda L: (X.conjugated() * L), self.L_s )
        r = map( ifft, R)
        r_argmax = abs(r).argmax()
        ( delta_f, ca_delay ) = (r_argmax / r.shape[1], r_argmax % r.shape[1] )

        return (delta_f, ca_delay) 




# - - - - -
    #def __get_local_code(self, delta_f):
    #    return self.L_s[delta_f+10]

    #def __get_param_matrix(self):
    #    m = 21; n = 5000
    #    ca = numpy.arange(0,m*n) % n
    #    df = (numpy.arange(0,m*n) % m) - 10
    #    df.shape = (n,m)

    #    return zip( df.transpose().ravel(), ca )
# - - - - -



class Tracking:
    """Tracking module.

    Calculates the fine frequency and track the signal to extract the naviagation message.
    """
    def __init__(self):
        pass

    def track(self, delta_f, ca_code_delay):
        pass


def main():
    space_vehicle = 1
    input = numpy.random.randn(5000)
    acq = Acquisition(1)
    (f_doppler, ca_delay ) = acq.search(input)

if __name__ == '__main__':
    main()


# vim: ts=4 sts=4 sw=4 sta et ai

