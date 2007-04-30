#    Copyright 2007 Trond Danielsen <trond.danielsen@gmail.com>
#
#    This file is part of OpenGNSS.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Boston, MA  02110-1301  USA

from numpy import *
from scipy import signal

import ca_code
import dft

import pylab as p


debug = True
def p_debug( string ):
    if debug == True:
        print string




class Acquisition:

    # Doppler frequency search range.
    doppler_search_step = 1e3
    doppler_search_min = -10e3
    doppler_search_max = 10e3
    doppler_range = arange(doppler_search_min, \
        doppler_search_max + doppler_search_step, \
        doppler_search_step)

    # Taken from tsui.
    threshold = 2.3*pi/5

    argmax_2d = lambda self, x: (x.argmax()/len(x.T), x.argmax() % len(x.T))


    def __init__(self, fs, svn):
        self.fs = fs
        self.svn = svn

        # Local code matrix
        (self.lc, self.LC) = self.local_code()
        self.N = len(self.lc.T)
        self.mydft = dft.DFT(self.fs)
        self.dft = self.mydft.calc


    def truncate(x, N):
        foo = len(x) % N
        if foo > 0:
            return x[:-foo]
        else:
            return x


    def local_code(self, shift=0):
        code = ca_code.ca_code(svn=self.svn, fs=self.fs, ca_shift=shift)
        f = lambda fd: array( [ e**(2j*pi*fd*n/self.fs) for n in range(len(code))] )
        lc = array( [code*f(fd) for fd in self.doppler_range ] )
        return ( lc, (fft.fft(lc)))


    def calc(self, x, n=5):
        f = lambda fd: array([ e**( -2j*pi*fd*n/self.fs) for n in arange(self.N)])

        # Filters.
        a = [1.0]
        b_coarse = signal.firwin( 60, 20e3/self.fs)
        b_medium = signal.firwin( 60, 1e3/self.fs)
        b_fine = signal.firwin( 60, 0.4e3/self.fs)

        # Truncate and reshape input signal.
        x = reshape ( self.truncate( x, self.N), (-1, self.N))[:n]

        # Coarse acquisition. 
        # Hvorfor virker conf(fft.fft naar fft.ifft ikke funker??
        X = conj(fft.fft(x))
        r = sum( array([ abs(fft.ifft( self.LC*X_i)) for X_i in X ]), axis=0)
        (f_coarse, ca_delay) = self.argmax_2d(r)
        f_coarse = self.doppler_range[ f_coarse ]
        p_debug( "Coarse f: %f Hz." % (f_coarse) )


        # Remove C/A code from input signal.
        x = x * ca_code.ca_code(svn=self.svn, fs=self.fs, ca_shift=ca_delay)

        # Mix down to f_coarse and reduce BW to 1kHz.
        x = x * f(f_coarse)
        x = signal.lfilter( b_coarse, a, x )

        # Medium resolution calculation.
        f_medium = arange(-400, 400+1, 400)
        Xk = [ abs(self.dft(x[0],f_i)) for f_i in f_medium ]
        f_medium = f_medium[ argmax(Xk) ]
        if x.ndim < 2:
            x = reshape(x, (1,-1))
        p_debug( "Medium f: %f Hz." % f_medium )

        # Mix down to f_medium and reduce BW to 400 Hz.
        x = x * f(f_medium)
        x = signal.lfilter( b_medium, a, x )


        # Fine frequency calculation.
        Xk = self.dft(x, f_medium)
        theta = angle(Xk)

        d_theta = array([ theta[n] - theta[n-1] for n in range(1, len(theta)) ])

        def foo_theta(d_theta):
            tmp = d_theta
            if abs(d_theta) > self.threshold:
                d_theta = tmp - 2*pi
                if abs(d_theta) > self.threshold:
                    d_theta = tmp + 2*pi
                    if abs(d_theta) > self.threshold:
                        d_theta = tmp - pi
                        if abs(d_theta) > self.threshold:
                            d_theta = tmp - 3*pi
                            if abs(d_theta) > self.threshold:
                                d_theta = tmp + pi
            return d_theta

        d_theta = array( map( foo_theta, d_theta))
        f_fine = d_theta.mean()/(2*pi*1e-3)
        p_debug( "Fine frequency: %f Hz." % f_fine )

        return (f_coarse + f_medium + f_fine, ca_delay)



# vim: ai ts=4 sts=4 et sw=4

