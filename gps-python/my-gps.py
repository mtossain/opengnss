from numpy import *

import pylab as p
from scipy import signal
from scipy import random

from ca_code import

# - Global variables -

# Doppler frequency search range.
doppler_search_step = 1e3
doppler_search_min = -10e3
doppler_search_max = 10e3
doppler_range = arange(doppler_search_min, \
    doppler_search_max + doppler_search_step, \
    doppler_search_step)

# Samping frequency.
fs = 2e6

# Signal to noise ratio.
SNR = -19.0 # dB

# Noise is 19 dB above the signal.
noise_ampl = 10**(-SNR/20.0)


# - Local funtions -

cross_corr = lambda x,y: \
    fft.ifft(fft.fft(x) * conj(fft.fft(y)))[:len(x)]
fd = lambda f, N: \
    array( [e**(2j*pi*f*n/fs ) for n in range(int(N))] )
power = lambda x: \
    10*log10(sum(abs(x)**2)/len(x))
argmax_2d = lambda x: \
    (x.argmax()/len(x[0]), x.argmax() % len(x[0]))
bpsk = lambda n, baud, fs: \
    signal.resample( filter(lam
bda x: x!= 0, random.randint(-1,2,n)), )
add_noise = lambda x, noise_ampl: \
    x + noise_ampl * random.randn(len(x)) * e**(2j*pi*random.randn(len(x)))




def acquisition(x, prn, n=3):

    ca = ca_code(prn).get()
    N = len(ca)

    # Local code matrix
    x_hat = array( map( lambda f: ca * fd(f, N), doppler_range))

    # Integrate signal.
    r_map = zeros((len(doppler_range),1e-3*fs))
    for _ in range(n):
        r_map = r_map + array( [cross_corr(y, x) for y in x_hat] )

    r_map = abs(r_map)

    # Extract maximum value from correlation map.
    (doppler_hat, ca_delay) =  argmax_2d(r_map)

    return (r_map, doppler_hat, ca_delay)


def plot(map):
    # Plot correlation results.
    if 1:
        p.figure()
        i = 1
        for y in map:
            p.subplot(len(map.T[0]),1,i)
            p.plot( y )
            p.axis([0, len(map[0]), map.min(), map.max()])
            p.yticks([])
            p.xticks([])
            p.ylabel("Doppler: %d" % (doppler_search_min + (i-1)*doppler_search_step), {'rotation': 'horizontal'})
            i += 1
        
    # Display plots.
    p.show()


def main():
    # Generate received signal, add unknown phase error.
    N = len(ca_code().get())
    x =  shift(ca_code(prn=1), 200)  * fd(-3.34e3, N) * e**(2j*pi*random.randn())
    x += shift(ca_code(prn=3), 1200) * fd(4.12e3,  N) * e**(2j*pi*random.randn())
    x += shift(ca_code(prn=2), 600)  * fd(1.871e3, N) * e**(2j*pi*random.randn())

    (r_map, doppler_hat, ca_delay) = acquisition(x, 1)

    print "Max val: %d" % r_map.max()
    print "Doppler frequency: %d" % (doppler_search_min + doppler_hat*doppler_search_step)
    print "C/A delay: %d" % ca_delay
    
    plot(r_map)

if __name__ == "__main__":
    main()
    
