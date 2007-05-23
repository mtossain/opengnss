#!/usr/bin/env python

from gnuradio import gr
from numpy import *
from gr_gnss import acquisition
from gps import ca_code
import pylab as p


class acquisition_test(gr.top_block):
    def __init__(self, alpha):
        gr.top_block.__init__(self, "acquisition_test")

        # Simulated signal.
        if 0:
            fs = 4e6
            fs_foo = fs
            code = ca_code(svn=1, fs=fs_foo, ca_shift=200)
            code = r_[ code, code, code, code, code, code ]
            code = r_[ code, code, code, code, code, code ]
            code = r_[ code, code, code, code, code, code ]
            code = r_[ code, code, code, code, code, code ]
            code = r_[ code, code]
#            f = array ( [ e**( 2j*pi*7e3*n/fs) for n in arange(len(code)) ] )
            f = e**( 2j*pi*7e3*(arange(len(code)))/fs_foo)
            x = code * f
            self.src = gr.vector_source_c( x )
        # Real signal.
        else:
            fs = 4e6
#            file_src =  gr.file_source(gr.sizeof_gr_complex, "../data/L1-2MHz-svn1.dat")
            file_src =  gr.file_source(gr.sizeof_gr_complex, "../data/L1-4MHz-svn1-nav.dat")
            self.src =  gr.skiphead( gr.sizeof_gr_complex, 4000 )
            self.connect( file_src, self.src)

        self.acquisition = acquisition(fs=fs, svn=1, alpha=alpha)

        self.ca_sink = gr.vector_sink_f()
        self.fd_sink = gr.vector_sink_f()
        self.rmax_sink = gr.vector_sink_f()

        self.connect( self.src,  self.acquisition)
        self.connect( (self.acquisition, 0), self.ca_sink )
        self.connect( (self.acquisition, 1), self.fd_sink )
        self.connect( (self.acquisition, 2), self.rmax_sink )


def main():
    alpha = 0.1
    top_block = acquisition_test(alpha)
    runtime = gr.runtime(top_block)

    try:
        runtime.start()
        runtime.wait()

        fig = p.figure()
        fig.subplots_adjust(hspace=0.4)

        p.subplot(3,1,1)
        p.plot( top_block.ca_sink.data())
        p.title("C/A code delay")
        p.xlabel("$t [ms]$")

        p.subplot(3,1,2)
        p.plot( top_block.fd_sink.data())
        p.title("Doppler frequency estimate.")
        p.xlabel("$t [ms]$")

        p.subplot(3,1,3)
        p.plot( top_block.rmax_sink.data())
        p.title("Correlation peak magnitude.")
        p.xlabel("$t [ms]$")

        p.show()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

# vim: ai ts=4 sts=4 et sw=4
