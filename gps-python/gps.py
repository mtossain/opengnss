#!/usr/bin/env python
import numpy, scipy
from scipy import signal
import cmath

f_sampling = 5e3
f_carrier = 1.25e6 

def shift(data, n=1):
    """Shift the vector."""
    return numpy.concatenate( (data[-n:], data[:-n]) )

class GPS:
    def __init__(self):
        """ """
        self.f_sampling = 5e3
        self.f_carrier = 1.25e6 

class Acquisition:
    def __init__(self, sv):
        """ """
        self.ca = CA(sv)

    def gen_local_code(self, delta_f, delay):
        """Generate local code from frequecy f and shifted ca code."""
        ca_code = shift( self.ca.get_code(), delay)
        carrier = numpy.array(map( (lambda n: cmath.exp( 2j*cmath.pi*(f_carrier+delta_f)*n )), range(0,5000) ))

        len(ca_code)
        len(carrier)

        return ca_code*carrier

    def search(self, gps_signal):
        """Search through all code delay chips and doppler shifts."""
        delta_f = numpy.arange(-10,11)
        ca_code_shifts = numpy.arange(0,5000)

        m = numpy.zeros ( (len(delta_f), len(ca_code_shifts) ), complex )

        R = lambda x: numpy.inner(gps_signal, self.gen_local_code( x[0],x[1]) )

        bla = map (R, m) 
        for m in delta_f:
            for n in ca_code_shifts:
                #m[m,n] =  numpy.inner( gps_signal, self.gen_local_code(m, n) )
                print numpy.inner( gps_signal, self.gen_local_code(m, n) )

        return ( (m.argmax()/m.shape[0]), (m.argmax() % m.shape[1]) )
        

# class Tracking:
    


class CA:
    """CA code generator"""
    def __init__(self, sv):
        self.ca_length = 1023
        self.code_delay_chips = [5,6,7,8,17,18,139,140,141,251,252,254,255,256,257,258,469,470,471,472,473,474,509,512,513,514,515,516,859,860,861,862]

        # G1 code generator polynom
        self.g1 = lambda reg: reg[2]*reg[9] 

        # G2 code generator polynom
        self.g2 = lambda reg: reg[1]*reg[2]*reg[5]*reg[7]*reg[8]*reg[9] 
        self.set_shift(sv)
    
    def set_shift(self, sv):
        """Set correct CA chip delay corresponding to the desired SV."""
        self.shift = self.code_delay_chips[sv]

    def __g_code(self, code_function ):
        reg = -1*numpy.ones(10)
        g = numpy.empty(self.ca_length)

        for i in range(0,self.ca_length):
            g[i] = reg[9]
            save = code_function(reg)
            reg[1:10] = reg[0:9]
            reg[0] = save
        return signal.signaltools.resample(g, 5000)

    def get_code(self):
        """Returns the desired CA code."""
        return -( self.__g_code(self.g1) * shift(self.__g_code(self.g2), self.shift))


def main():
    space_vehicle = 1
    input = numpy.random.randn(5000)
    acq = Acquisition(1)
    acq.search(input)

if __name__ == '__main__':
    main()


# vim: ts=4 sts=4 sw=4 sta et ai

