#
#

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

