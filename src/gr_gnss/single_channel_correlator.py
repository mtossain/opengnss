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
from local_code import local_code
import os


class single_channel_correlator(gr.hier_block2):
    def __init__(self, fs, fd, svn, alpha, dump_bins=False):
        fft_size = int( 1e-3*fs)

        gr.hier_block2.__init__(self,
            "single_channel_correlator",
            gr.io_signature(1,1, gr.sizeof_gr_complex*fft_size),
            gr.io_signature(1,1, gr.sizeof_float*fft_size))

        lc = local_code(svn=svn, fs=fs, fd=fd)
        mult = gr.multiply_vcc(fft_size)
        ifft = gr.fft_vcc(fft_size, False, [])
        mag = gr.complex_to_mag_squared(fft_size)
        self.iir = gr.single_pole_iir_filter_ff( alpha, fft_size)

        self.connect( self, (mult, 0))
        self.connect( lc,   (mult, 1))
        self.connect( mult, ifft, mag, self.iir, self)

        if dump_bins == True:
            self.connect_debug_sink(self.iir,fft_size,'/home/trondd/opengnss_output', fd)


    def set_alpha(self, alpha):
        self.iir.set_taps(alpha)


    def connect_debug_sink(self, src, fft_size, output_path, fd):
        filename = os.path.join(output_path, "fd_%d.dat" % fd)
        file_sink = gr.file_sink(fft_size*gr.sizeof_float, filename)
        self.connect( src, file_sink )


# vim: ai ts=4 sts=4 et sw=4
