from operator import xor
from numpy import *
from scipy.signal import resample

class ca_code:
    """Foo
    """
    shift = lambda l, n: \
        r_[ l[	n:], l[:n]]

    g1_gen = lambda _, reg: (reg>>9 ^ reg>>2) | (reg<<1)
    g1_taps = (10,)
    g2_gen = lambda _, reg: \
        (reg>>9 ^ reg>>8 ^ reg>>7 ^ reg>>5 ^ reg>>2 ^ reg>>1) | (reg<<1)
    g2_taps = [ (2,6), (3,7), (4,8), (5,9) ] # Not complete!

    def __init__(self, prn=1, fs=2e6):
        """C/A code generator."""
        self.code_length = 1e-3 # ms
        self.prn = prn
        tap = lambda reg, taps: reduce(xor, [ reg>>n for n in taps])
        rs = lambda x: resample(x, self.code_length*fs)

        g1 = 0xffff
        g2 = 0xffff
        ca = []
        for _ in range(2**10-1):
            g1 = self.g1_gen(g1)
            g2 = self.g2_gen(g2)
            ca += [ (tap(g1, self.g1_taps) ^ tap(g2, self.g2_taps[self.prn])) & 0x01] # Extract lsb.
        self.ca_raw = ca
        self.code = array(
            map( sign, # Normalize after resampling
            rs( # Resample
            map( lambda x: (x-0.5)/0.5, ca)))) # Normalize.
        
    def get(self):
        return self.code


# vim: ai ts=4 sts=4 et sw=4
