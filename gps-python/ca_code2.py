from numpy import *
#from scipy.signal import resample

def ca_code(svn=1):
    # Length of the CA code.
    N = 2**10-1

    # Shift an array n spaces.
    shift = lambda l, n: r_[ l[	n:], l[:n]]
    
    # MLS feedback registers
    g1_gen = lambda reg: ((reg>>9 ^ reg>>2) & 0x01 ) | (reg<<1 & N)
    g2_gen = lambda reg: ((reg>>9 ^ reg>>8 ^ reg>>7 ^ reg>>5 ^ reg>>2 ^ reg>>1) & 0x01) | (reg<<1 & N)

    # List of all G2 shifts.
    svn_shift = [5]

    # Inital Register settings, all ones.
    g1 = empty(N, dtype=int)
    g1[0] = N
    g2 = empty(N, dtype=int)
    g2[0] = N

    for i in range(1,N):
        g1[i] = g1_gen(g1[i-1])
        g2[i] = g2_gen(g2[i-1])

    # Create C/A code by 
    return ((g1>>9) ^ ( shift(g2, -svn_shift[svn-1])>>9)) & 0x01

def qa_ca_code():
    bitlist_to_oct = lambda x: sum([x[len(x)-1-i] << i for i in range(len(x))])

    ca_1 = 01440

    assert alltrue( bitlist_to_oct(ca_code(1)[:10]) == ca_1)

if __name__ == '__main__': 
    qa_ca_code()
    print ca_code()[:20]

# vim: ai ts=4 sts=4 et sw=4
