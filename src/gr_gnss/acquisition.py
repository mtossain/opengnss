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

from gnuradio import gr
from single_channel_correlator import *


class acquisition(gr.hier_block2):
    # Output 0 is the C/A code delay.
    # Output 1 is the Doppler frequency estimate in Hz.
    # Output 2 is the correlation peak value.

    def __init__(self, fs, svn, alpha, fd_range, dump_bins=False):
        gr.hier_block2.__init__(self,
            "acquisition",
            gr.io_signature(1,1, gr.sizeof_gr_complex),
            gr.io_signature(3,3, gr.sizeof_float))

        fft_size = int( 1e-3*fs)
        doppler_range = self.get_doppler_range(fd_range)

        agc = gr.agc_cc( 1.0/fs, 1.0, 1.0, 1.0)
        s2v = gr.stream_to_vector(gr.sizeof_gr_complex, fft_size)
        fft = gr.fft_vcc(fft_size, True, [])

        argmax = gr.argmax_fs(fft_size)
        max = gr.max_ff(fft_size)

        self.connect( self, s2v, fft)
        self.connect( (argmax, 0),
                gr.short_to_float(),
                (self, 0))
        self.connect( (argmax,1),
                gr.short_to_float(),
                gr.add_const_ff(-fd_range),
                gr.multiply_const_ff(1e3),
                (self,1))
        self.connect( max, (self, 2))

        # Connect the individual channels to the input and the output.
        self.correlators = [ single_channel_correlator( fs, fd, svn, alpha, dump_bins) for fd in doppler_range ]

        for (correlator, i) in zip( self.correlators, range(len(self.correlators))):
            self.connect( fft, correlator )
            self.connect( correlator, (argmax, i) )
            self.connect( correlator, (max, i) )


    def set_alpha(self, alpha):
        for correlator in self.correlators:
            correlator.set_alpha(alpha)


    def get_doppler_range(self, fd_range):
        """Range is given in kHz. 
        Step length is currently hard coded to 1kHz."""
        step = 1e3
        return range( int(-fd_range*1e3), int((fd_range+1)*1e3), int(step))

# vim: ts=4 sts=4 sw=4 sta et ai

