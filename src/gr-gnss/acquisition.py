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

from gnuradio import gr,window,gr_max
from local_code import local_code
from numpy import *

class single_channel_correlator(gr.hier_block2):
    def __init__(self, fs, fd, svn):
        self.fft_size = int( 1e-3*fs)
        self.window = window.blackmanharris(self.fft_size)

        # aliases:
        c = lambda i, o, ip=0, op=0: self.connect(i,ip,o,op)
        d = lambda n, f: self.define_component( n, f)

        gr.hier_block2.__init__(self,
            "foo",
            gr.io_signature(1,1, gr.sizeof_gr_complex*self.fft_size),
            gr.io_signature(1,1, gr.sizeof_float*self.fft_size))

        # Local code.
        d( "local_code", local_code(svn=svn, fs=fs, fd=fd))

        # Multiply local code with recv. signal.
        d( "mult", gr.multiply_vcc(self.fft_size))

        # Invers transform result.
        d( "ifft", gr.fft_vcc(self.fft_size, False, self.window))

        # Get signal magnitude.
        d( "mag", gr.complex_to_mag(self.fft_size) )

        # Integrate signal.
        # alpha=0.2 is chosen on an ad-hoc basis, 
        # but the signal is stable after 10 periods.
        d( "iir", gr.single_pole_iir_filter_ff( 0.2, self.fft_size))

        c( "self", "mult" )
        c( "local_code", "mult", op=1 )
        c( "mult", "ifft")
        c( "ifft", "mag" )
        c( "mag", "iir" )
        c( "iir", "self")


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
            gr.io_signature(2,2, gr.sizeof_short))

        # aliases:
        c = lambda i, o, ip=0, op=0: self.connect(i,ip,o,op)
        d = lambda n, f: self.define_component( n, f)

        # Input signal; get Fourier transform of signal.
        d( "input_s2v", gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size))
        d( "input_fft", gr.fft_vcc(self.fft_size, True, self.window))
        c( "self", "input_s2v" )
        c( "input_s2v", "input_fft" )

        # C/A delay processing.
        d( "ca_sum", gr.add_vff(self.fft_size))
        d( "ca_iir", gr.single_pole_iir_filter_ff( 0.02, self.fft_size))
        d( "ca_argmax", gr_max.argmax_fs(self.fft_size))
        c( "ca_sum", "ca_iir" )
        c( "ca_iir", "ca_argmax" )
        c( "ca_argmax", "self", op=0 )

        # Fd processing.
        d( "fd_interleave", gr.interleave(gr.sizeof_float))
        d( "fd_s2v", gr.stream_to_vector(gr.sizeof_float, len(self.doppler_range)))
        d( "fd_iir", gr.single_pole_iir_filter_ff( 0.02, len(self.doppler_range)))
        d( "fd_argmax", gr_max.argmax_fs(len(self.doppler_range)))
        c( "fd_interleave", "fd_s2v" )
        c( "fd_s2v", "fd_iir" )
        c( "fd_iir", "fd_argmax" )
        c( "fd_argmax", "self", op=1 )

        # Connect the individual channels to the input and the output interleaver.
        for (fd, i) in zip( self.doppler_range, range(len(self.doppler_range))):
            d( "correlator_%d" % fd, single_channel_correlator(fs, fd, svn))
            d( "fd_max_%d" % fd, gr_max.max_ff(self.fft_size))

            # Connect input to correlators.
            c( "input_fft", "correlator_%d" % fd )

            # Connect to C/A processing.
            c( "correlator_%d" % fd, "ca_sum", op=i )

            # Connect correlators to Fd processing.
            c( "correlator_%d" % fd, "fd_max_%d" % fd )
            c( "fd_max_%d" % fd, "fd_interleave", op=i )

# vim: ts=4 sts=4 sw=4 sta et ai

