#all import below
import numpy as np
import math
import struct
import array
import time
import DSP
import wave
import os
import function
import RingBuffer
from scipy.signal import hilbert

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-27"
__version__="1.0-dev"


# store MFFC coefficients in a ring buffer during data acquisition 
class MFFCsRingBuffer(object):
        """ Initialize the ring buffer"""
        def __init__(self):
            self.__data=np.zeros(1950)
            self.__length=1950
            self.__index=0
            self.__tail=0
            self.__count=0
            self.__cond=0# condition in EndSegments
            self.__flag="out"
            self.__numberOfWindowRejection=20 # 1600 samples -> need to modify it eventually
            self.__lengthOfWindowMinima=150 # need to adapt this value 10*13
            self.__EnergyCoeffArray=np.empty(13,'f')
            self.__SampleRingBuffer=RingBuffer.RingBuffer(24000,200,85)
            self.__previous_amplitude_envelope=0.
                
        def extend(self,data):
            data_index=(self.__index+np.arange(data.size))
            if np.all(self.__data[data_index]==np.zeros(len(data_index))) :
                    self.__data[data_index]=data
                    self.__index=data_index[-1]+1
                    if self.__index >= self.__length :
                            print("fatal Error : segment too long")
            else :
                    print("Error : RingBuffer is overwritten ")
        def extend2(self,data):
            data_index=(self.__tail+np.arange(data.size))
            if np.all(self.__data[data_index]==np.zeros(len(data_index))) :
                    self.__data[data_index]=data
                    self.__tail=data_index[-1]+1
                    if self.__tail >= self.__length :
                            print("fatal Error : segment too long")
            else :
                    print("Error : RingBuffer is overwritten ")
        
        def get(self):
                #new version #
                idx=(0+np.arange(self.__tail))
                temp=np.array(self.__data[idx])
                ######### NEW add 2017.05.11 #####
				# comment 20 05 2017 MFCCsN=DSP.FeatureNormalization(temp)
                MFCCs=temp.reshape((len(idx)/13),13).T
                ######### END NEW add ####### NORMALIZATION ####
                delta=function.deltaMFCCs(MFCCs,9)
                deltaDelta=function.deltaMFCCs(delta,9)
                mfccs=np.concatenate((MFCCs,delta,deltaDelta),axis=0)
                mfccs_reshape=mfccs.reshape(mfccs.size,order='F')
                
                ####### old version ######
              #  temp=np.array(self.__data).reshape((150,13)).T
              #  delta=function.deltaMFCCs(temp,9)
              #  deltaDelta=function.deltaMFCCs(delta,9)
              #  mfccs=np.concatenate((temp,delta,deltaDelta),axis=0)
              #  np.savetxt('mfcc.out',mfccs)
                self.__data=np.zeros(1950)
                self.__index=0
                self.__tail=0
                self.__out="out"
         #       print "tail :" ,self.__tail , "new value ;" , self.__tail/13 
                return np.concatenate((mfccs_reshape,np.zeros(self.__length*3-mfccs_reshape.size)),axis=0),self.__SampleRingBuffer.getSegments(self.__tail/13)

        def flag(self,data,threshold,entropyDistance,entropyThresh,coeff,energy, AudioSample):
                # first case
                if (data<threshold or entropyDistance<entropyThresh)  and self.__flag=="rejeted" :
                        self.__flag="out"
                        
                if (data<threshold or entropyDistance<entropyThresh) and self.__flag=="admit" :
                        self.__flag="out"
                        
                if (data>=threshold and entropyDistance>=entropyThresh) and self.__flag=="out" :
                        self.__flag="in"
                        self.__SampleRingBuffer.initialize()
                        
                if (data<threshold and entropyDistance<entropyThresh) and self.__flag=="in" :
                        self.__flag="io"

                if (data>=threshold and entropyDistance>=entropyThresh) and self.__flag=="io" :
                        self.__flag="in"

                if self.__flag=="in" or self.__flag=="io" :
                        self.__EnergyCoeffArray[0]=energy
                        self.__EnergyCoeffArray[1+np.arange(12)]=coeff[1+np.arange(12)]
                        
                if self.__flag=="in" :
                        self.__tail=self.__index
                        self.extend(self.__EnergyCoeffArray)
                        self.__SampleRingBuffer.extendSegments(AudioSample)
                        self.__count=0
                        self.__cond=0
                        self.__previous_amplitude_envelope=np.sum(np.abs(hilbert(AudioSample)))
                        
                if self.__flag=="io" :
                        self.__cond,self.__tail,self.__previous_amplitude_envelope =DSP.EndSegments(self.__cond,self.__previous_amplitude_envelope,self.__index,self.__tail, AudioSample)
                        #print(self.__tail)
                        #print(self.__previous_amplitude_envelope)
                        if self.__count <=self.__numberOfWindowRejection :
                                self.__count+=1
                                self.extend( self.__EnergyCoeffArray)
                                self.__SampleRingBuffer.extendSegments(AudioSample)
                        else :
                                delete_index=(self.__tail+np.arange(self.__index-self.__tail))
                                self.__data[delete_index]=0.
                                self.__count=0
                           #     print(self.__index)
                                self.__flag="done"
                                self.__index=0

                if self.__flag=="done" :
                        if self.__tail< self.__lengthOfWindowMinima :
                                self.__flag="rejeted"
                                self.__data=np.zeros(1950)
                        else :
                                self.__flag="admit"

                return self.__flag
                                
                
