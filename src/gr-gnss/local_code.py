from gnuradio import gr,window
from numpy import *
from gps_python.ca_code import ca_code

class local_code(gr.hier_block2):
    def __init__(self, svn, fs, fd):

        # aliases:
        c = lambda i, o: self.connect(i,0,o,0)
        d = lambda n, f: self.define_component( n, f)

        code = ca_code(svn=svn, fs=fs)
        fd = array( [ e**(2j*pi*fd*n/fs) for n in range(len(code))] )
        lc = conj(fft.fft(code * fd))

        gr.hier_block2.__init__(self,
            "local_code",
            gr.io_signature(0,0,0),
            gr.io_signature(1,1, len(lc)*gr.sizeof_gr_complex))

        d( "code", gr.vector_source_c(lc, True))
        d( "s2v", 
            gr.stream_to_vector(gr.sizeof_gr_complex, len(lc)))
        c( "code", "s2v" )
        c( "s2v", "self" )


