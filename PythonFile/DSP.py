# all import here
import alsaaudio as alsa
from multiprocessing import Process, Queue 
import numpy as np
import math
import struct
import array
import time
import numpy.fft
from scipy.signal import hilbert

__author__="Quentin MASCRET <quentin.mascret.1 ulaval.ca>"
__date__="2017-04-14"
__version__="1.0-dev"

THRESHOLD=0.1
""" Normalize the audio samples from an array of integers"""
def normalize(data,max_value) :
    data=np.array(data)
    #biais=int(0.5 * max_value)
    fac=1.0/(max_value)
    data=fac * (data)#- biais )
    return data

def threshold(data):
    # return 'true' if below the 'silent' threshold
    data=np.array(data)
    for i in range (0,len(data)) :
        if data[i]<= 200 and data[i]>=-200 :
            data[i]=0.
    return data
  #  print(data)

def EndSegments(cond,previous_amplitude_envelope,currIndex,tail, AudioSample):
    current_amplitude_envelope=np.sum(np.abs(hilbert(AudioSample)))
    if  previous_amplitude_envelope >= current_amplitude_envelope and cond<=3: # need cond three times to have good portion of data
        currTail=currIndex
    else :
        currTail=tail
        cond+=1
    return cond, currTail , current_amplitude_envelope



    
def logEnergy(frame):
    nfft=256 # the nextpow of 200 samples
    fft = numpy.fft.rfft(frame, nfft)
    # Square of absolute value
    power = fft.real * fft.real + fft.imag * fft.imag
    return np.log(np.sum(power))

    """
    Denormalize the data from an array of floats with unity level into an array of integers.
    """
def denormalize(data, max_val):
       # bias = int(0.5 * max_val)
        fac = max_val
        data = np.array(data)
        data = (fac * data)#.astype('H') + bias
        return data

def FeatureNormalization(mfcc):
    MfccMean=np.mean(mfcc)
    MfccStd=np.std(mfcc)
    return np.array((mfcc-MfccMean)/MfccStd)


