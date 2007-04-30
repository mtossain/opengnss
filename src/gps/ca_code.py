from numpy import *
from scipy.signal import resample

def ca_code(svn=1, fs=0, ca_shift=0):
    # Length of the CA code.
    N = 2**10-1

    # Shift an array n spaces.
    shift = lambda l, n: r_[ l[	n:], l[:n]]
    
    # MLS feedback registers
    g1_gen = lambda reg: ((reg>>9 ^ reg>>2) & 0x01 ) | (reg<<1 & N)
    g2_gen = lambda reg: ((reg>>9 ^ reg>>8 ^ reg>>7 ^ reg>>5 ^ reg>>2 ^ reg>>1) & 0x01) | (reg<<1 & N)

    # List of all G2 shifts.
    g2_chip_delay = \
        [5,6,7,8,17,18,139,140,141,251,252,254,  \
        255,256,257,258,469,470,471,472,473,474, \
        509,512,513,514,515,516,859,860,861,862]

    # Inital Register settings, all ones.
    g1 = empty(N, dtype=int)
    g1[0] = N
    g2 = empty(N, dtype=int)
    g2[0] = N

    for i in range(1,N):
        g1[i] = g1_gen(g1[i-1])
        g2[i] = g2_gen(g2[i-1])

    # Create C/A
    ca = ((g1>>9) ^ ( shift(g2, -g2_chip_delay[svn-1])>>9)) & 0x01
    
    # Convert to bi-phase psk
    ca = ca*2 -1
    
    # Resample if fs is given.
    if fs:
#         ca1 = array ( map( sign, resample( ca, 1e-3*fs)))
        gr = 1.023e6
        k = gr*arange(1e-3*fs)/fs
        k = map( int, k)
        ca = ca[k]

    return shift(ca, ca_shift)


def qa_ca_code():
    bitlist_to_oct = lambda x: sum([x[len(x)-1-i] << i for i in range(len(x))])

    ca_1 = 01440

    assert alltrue( bitlist_to_oct(ca_code(1)[:10]) == ca_1)


# vim: ai ts=4 sts=4 et sw=4
