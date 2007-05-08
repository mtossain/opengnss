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

from gnuradio import gr,window
from local_code import local_code
from numpy import *

class single_channel_correlator(gr.hier_block2):
    def __init__(self, fs, fd, svn):
        self.fft_size = int( 1e-3*fs)
        self.window = window.blackmanharris(self.fft_size)

        # aliases:
        c = lambda i, o, ip=0, op=0: self.connect(i,ip,o,op)
        #d = lambda n, f: self.define_component( n, f)

        gr.hier_block2.__init__(self,
            "foo",
            gr.io_signature(1,1, gr.sizeof_gr_complex*self.fft_size),
            gr.io_signature(1,1, gr.sizeof_float*self.fft_size))

        # Local code.
        self.local_code = local_code(svn=svn, fs=fs, fd=fd)

        # Multiply local code with recv. signal.
        self.mult = gr.multiply_vcc(self.fft_size)

        # Invers transform result.
        self.ifft = gr.fft_vcc(self.fft_size, False, self.window)

        # Get signal magnitude.
        self.mag = gr.complex_to_mag(self.fft_size)

        # Integrate signal.
        # alpha=0.2 is chosen on an ad-hoc basis, 
        # but the signal is stable after 10 periods.
        self.iir = gr.single_pole_iir_filter_ff( 0.2, self.fft_size)

        self.connect( self, (self.mult, 0))
        self.connect( self.local_code, (self.mult, 1))

        self.connect( self.mult, self.ifft, self.mag, self.iir, self)


class acquisition(gr.hier_block2):

    # Doppler frequency search range.
    doppler_search_step = 1e3
    doppler_search_min = -10e3
    doppler_search_max = 10e3
    doppler_range = arange(doppler_search_min, \
        doppler_search_max + doppler_search_step, \
        doppler_search_step)

    def __init__(self, fs, svn):

        self.fft_size = int( 1e-3*fs)
        self.window = window.blackmanharris(self.fft_size)

        gr.hier_block2.__init__(self,
            "acquisition",
            gr.io_signature(1,1, gr.sizeof_gr_complex),
            gr.io_signature(2,2, gr.sizeof_int))

        # Input signal; get Fourier transform of signal.
        self.input_s2v = gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
        self.input_fft = gr.fft_vcc(self.fft_size, True, self.window)
        self.connect( self, self.input_s2v, self.input_fft)

        self.argmax = gr.argmax_fi(self.fft_size)
        map( lambda i: self.connect( (self.argmax, i), (self, i)), [0,1])

        # Connect the individual channels to the input and the output interleaver.
        self.correlators = [ single_channel_correlator( fs, fd, svn) for fd in self.doppler_range ]

        for (correlator, i) in zip( self.correlators, range(len(self.correlators))):
            self.connect( self.input_fft, correlator )
            self.connect( correlator, (self.argmax, i) )


# vim: ts=4 sts=4 sw=4 sta et ai

