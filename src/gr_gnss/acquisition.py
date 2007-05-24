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
    def __init__(self, fs, fd, svn, alpha):
        self.fft_size = int( 1e-3*fs)
        self.window = window.blackmanharris(self.fft_size)

        gr.hier_block2.__init__(self,
            "single_channel_correlator",
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
        self.iir = gr.single_pole_iir_filter_ff( alpha, self.fft_size)

        self.connect( self, (self.mult, 0))
        self.connect( self.local_code, (self.mult, 1))

        self.connect( self.mult, self.ifft, self.mag, self.iir, self)

        # Debug sink.
        self.file_sink = gr.file_sink(self.fft_size*gr.sizeof_float, "/home/trondd/opengnss_output/fd_%d.dat" % fd)
        self.connect( self.iir, self.file_sink)

class acquisition(gr.hier_block2):

    # Doppler frequency search range.
    doppler_search_step = 1e3
    doppler_search_min = -20e3
    doppler_search_max = 20e3
    doppler_range = arange(doppler_search_min, \
        doppler_search_max + doppler_search_step, \
        doppler_search_step)

    def __init__(self, fs, svn, alpha):

        self.fft_size = int( 1e-3*fs)
        self.window = window.blackmanharris(self.fft_size)

        gr.hier_block2.__init__(self,
            "acquisition",
            gr.io_signature(1,1, gr.sizeof_gr_complex),
            gr.io_signature(3,3, gr.sizeof_float))

        # Input signal; get Fourier transform of signal.
        agc = gr.agc_cc(1e3/fs,            # Time constant
                        1.0,               # Reference power
                        1.0,               # Initial gain
                        1.5)               # Maximum gain

        s2v = gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
        self.src = gr.fft_vcc(self.fft_size, True, self.window)
        self.connect( self, agc, s2v, self.src)

        self.argmax = gr.argmax_fs(self.fft_size)

        # Get correlation peak magnitude.
        self.max = gr.max_ff(self.fft_size)
        rmax_filt_coeffs = gr.firdes_low_pass( 1,
                1e3, # output rate, new value each ms.
                5, # max frequency change is 1 hz pr sec.
                50)
        self.connect( self.max,
#                gr.fir_filter_fff( 1, rmax_filt_coeffs),
#                gr.multiply_const_ff( 1.0/self.fft_size),
                (self, 2))

        # Connect C/A code estimate to output.
        ca_filt_coeffs = gr.firdes_low_pass( 1,
                1e3, # output rate, new value each ms.
                100, # max frequency change is 1 hz pr sec.
                50)
        self.connect( (self.argmax, 0),
                gr.short_to_float(),
                #gr.fir_filter_fff( 1, ca_filt_coeffs),
                (self, 0))

        fd_filt_coeffs = gr.firdes_low_pass( 1,
                1e3, # output rate, new value each ms.
                5, # max frequency change is 1 hz pr sec.
                100)

        self.connect( (self.argmax,1), 
                gr.short_to_float(),
                # Scale signal
                gr.multiply_const_ff( int(self.doppler_search_step )),
                gr.add_const_ff( int(self.doppler_search_min )),
#                gr.fir_filter_fff( 1, fd_filt_coeffs),
                (self,1))

        # Connect the individual channels to the input and the output.
        self.correlators = [ single_channel_correlator( fs, fd, svn, alpha) for fd in self.doppler_range ]

        for (correlator, i) in zip( self.correlators, range(len(self.correlators))):
            self.connect( self.src, correlator )
            self.connect( correlator, (self.argmax, i) )
            self.connect( correlator, (self.max, i) )


# vim: ts=4 sts=4 sw=4 sta et ai

