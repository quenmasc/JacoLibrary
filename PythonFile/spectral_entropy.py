# Copyright (c) 2017 Laval University
#
# You may copy and modify this freely under the same terms

__author__ = "Quentin Mascret <quentin.mascret.1@ulaval.ca>"
__version__ = "1.0.0-dev"
__date__ ="07.04.2017"

import numpy as np
import numpy.fft
from scipy import signal
import math
import time


class SPECTRAL_ENTROPY(object):
    def __init__(self, wlen=0.025, wshift=0.001, samplerate=8000,
                 nfft=256, p=0.96, alpha=0.96):
        # store parameter
        self.wlen = int(wlen * samplerate)
        self.wshift = int(wshift * samplerate)
        self.p = p
        self.nfft = nfft

        self.samplerate = samplerate

        # build hanning window
        self.win = numpy.hamming(self.wlen)

        # prior sample for preemphasis
        self.alpha = alpha
        self.prior = 0

    def pre_emphasis(self, frame):

        """Pre-emphasis signal in order to"""
        outfr = numpy.empty(len(frame), 'd')
        outfr[0] = frame[0] - self.alpha * self.prior
        for i in range(1, len(frame)):
            outfr[i] = frame[i] - self.alpha * frame[i - 1]
        self.prior = frame[-1]
       # print "frame" , frame , "value", outfr
        return outfr
    
    def frame2periodogram(self, frame):

        """Calculate Power Spectral Density of the frame via squaring its amplitude and 
                                                                            normalizing by the numbers of bins"""
        f, Pxx_den = signal.periodogram(self.pre_emphasis(frame), self.samplerate, self.win, self.nfft,
                                        detrend='constant', return_onesided=True, scaling='density', axis=-1)

        # Normalize the calculated PSD do that it can be viewed as a probability Density function (equal to 1)
        Normalize_PSD = Pxx_den / np.sum(Pxx_den)
        log_p = numpy.empty(len(Normalize_PSD), 'd')
        p = numpy.empty(len(Normalize_PSD), 'd')
        # Power Spectral Entropy
        eps = 2.220446049250313e-16
        entropy=0
        for i in range(0,len(Normalize_PSD)) :
            log_p[i] = math.log(Normalize_PSD[i]+eps,2)
            p[i]=Normalize_PSD[i]+eps
            entropy+=p[i]*log_p[i]
        return -entropy

    def SpectralEntropy(self,x, numberOfBlock=100,eps = 2.220446049250313e-16):
        L=len(x)
        EoL=np.sum(np.power(x,2))
        subWin = int(np.floor(L/numberOfBlock))
        if L!=subWin*numberOfBlock :
            print("correct length or number of block please")
        subWindows=x.reshape(subWin,numberOfBlock,order='F').copy()
        s=np.sum(subWindows**2, axis=0)/(EoL+eps)
        En=-np.sum(s*np.log2(s+eps))
        return En

   
