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



# vim: ai ts=4 sts=4 et sw=4
