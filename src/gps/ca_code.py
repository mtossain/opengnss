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

from numpy import *
from scipy.signal import resample

def ca_code(svn=1, fs=0, ca_shift=0, bpsk=True):
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

    # Convert to bpsk
    if bpsk == True:
        ca = ca*2 -1

    # Resample if fs is given.
    if fs:
        k = array(map( int, linspace(0, N-1, num=1e-3*fs)))
        ca = ca[k]
    return shift(ca, ca_shift)


def qa_ca_code():
    import sys
    bitlist_to_oct = lambda x: sum([x[len(x)-1-i] << i for i in range(len(x))])

    ca = [ 01440, 01620, 01710, 01744, 01133, 01454 ]

    for (ca_i,i) in zip(ca, range(1, len(ca))):
        try:
            assert alltrue( bitlist_to_oct(ca_code(i, bpsk=False)[:10]) == ca_i)
        except AssertionError:
            sys.exit("C/A code for SVN %d failed test!" % i)

    print "All C/A code tests passed."



# vim: ai ts=4 sts=4 et sw=4
