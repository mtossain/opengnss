#!/usr/bin/env python

from gnuradio import gr
from numpy import *
from gr_gnss import acquisition

class test_gps(gr.hier_block2):
    def __init__(self):

        gr.hier_block2.__init__(self,
            "test",
            gr.io_signature(0,0,0),
            gr.io_signature(0,0,0))

        self.src =  gr.file_source(gr.sizeof_gr_complex, "../data/L1-4MHz-svn1-nav.dat")
        self.head =  gr.skiphead( gr.sizeof_gr_complex, 2000 )
        self.acquisition = acquisition(fs=4e6, svn=1)
        self.ca_sink = gr.file_sink( gr.sizeof_int, "../outp/ca_sink.dat")
        self.fd_sink = gr.file_sink( gr.sizeof_int, "../outp/fd_sink.dat")

        self.connect( self.src, self.head, self.acquisition)
        self.connect( (self.acquisition, 1), self.fd_sink )
        self.connect( (self.acquisition, 0), self.ca_sink )


if __name__ == "__main__":
    try:
        gr.runtime(test_gps()).run()
    except KeyboardInterrupt:
        pass
