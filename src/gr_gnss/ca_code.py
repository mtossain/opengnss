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
from numpy import *
from scipy.signal import resample
from gps import ca_code

class ca_code(gr.hier_block2):

    def __init__(self, svn, fs):
        """
        """

        gr.hier_block2.__init__( self,
            "ca_code",
            gr.io_signature( 0,0,0),
            gr.io_signature( 1,1,gr.sizeof_float))

        self._svn = svn
        self._code = self.generate_code(svn, fs)

        self.define_component("code", gr.vector_source_f(self._code, True))
        self.connect( "code", 0, "self", 0)

