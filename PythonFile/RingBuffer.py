# all import here
import alsaaudio as alsa
from multiprocessing import Process, Queue 
import numpy as np
import math
import struct
import array
import time
import DSP
import wave
import os
from threading import Thread


__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-14"
__version__="1.0-dev"

# RING BUFFER #
class RingBuffer(object):

    """  Initialize ring buffer """
    def __init__(self,length,window_sample,step_sample):
        self.__data=np.zeros(length)
        self.__index=0
        self.__length=length
        self.__window=window_sample
        self.__step=step_sample
        self.__shift=0 # index for get
        self.__clean=0
        self.__flag=0
        self.__offsetIndex=((window_sample-step_sample)+np.arange(step_sample))

        
    """ Add data to the ring buffer -> data is anarray of float I suppose """
    def extend(self,data):
        data_index=(self.__index + np.arange(data.size))
        if np.all(self.__data[data_index]==np.zeros(len(data_index))) :
            self.__data[data_index]=data
            self.__index=data_index[-1]+1
            self.__index=self.__index%self.__length
        else :
            print("Error : RingBuffer is overwritten ")

    def extendSegments(self,data):
        if self.__flag==0 :
            self.__flag+=1
            data_index=(self.__index+np.arange(data.size))
        else :
            data_index=(self.__index+np.arange(self.__step))
        if np.all(self.__data[data_index]==np.zeros(len(data_index))) :
            if self.__flag==0:
                self.__data[data_index]=data
            else :
                self.__data[data_index]=data[self.__offsetIndex]
        self.__index=data_index[-1]+1
                
    """ get data from ring buffer FIFO -> idea : get working window at each time"""
    def get(self):
        idx=(self.__shift + np.arange(self.__window))
        idx_clean=(self.__clean + np.arange(self.__step))
        if self.__shift+self.__window > self.__length :
            temp_end=(np.arange(self.__shift,self.__length))
            temp_beg=(0+np.arange(self.__window-temp_end.size))
            idx= np.concatenate([temp_end,temp_beg])
        self.__shift+=self.__step
        self.__clean+=self.__step
        if self.__shift >= self.__length :
            self.__shift=self.__shift-self.__length
        if self.__clean >= self.__length :
            self.__clean=self.__clean-self.__length
        temp=self.__data[idx]
        self.__data[idx_clean]=np.zeros(self.__step)
        return temp

    def getSegments(self,tail):
        return_Index=(0+np.arange((self.__window+(tail-1)*self.__step)))
        self.__flag=0
        self.__index=0
        temp=self.__data[return_Index]
        self.__data=np.zeros(self.__length)
        return temp

    def index(self):
        return self.__index

    def initialize(self):
        self.__data=np.zeros(self.__length)
