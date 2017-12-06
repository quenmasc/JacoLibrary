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
import Limiter
from threading import Semaphore , Lock


__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-27"
__version__="1.0-dev"


# store MFFC coefficients in a ring buffer during data acquisition 
class MFFCsRingBuffer(object):
        """ Initialize the ring buffer"""
	def __init__(self):
			self.__data=np.zeros((2600),'f')
			self.__length=2600
			self.__lengthMax=1560
			self.__head=0
			self.__tail=0
            
            # flag parameters
			self.__count=0
			self.__cond=0 # condition in EndSegments
			self.__flag="out"
			self.__numberOfWindowRejection=20 # 1600 samples -> need to modify it eventually // 40
			self.__lengthOfWindowMinima=300 # need to adapt this value 10*13
			self.__EnergyCoeffArray=np.empty(13,'f')
			#   self.__SampleRingBuffer=RingBuffer.RingBuffer(24000,200,80)
			self.__previous_amplitude_envelope=0.
			self.__Env=Limiter._Limiter()
			self.__Lock=Lock()
	
			#semaphore & Lock
			self.__RessourceAccess= Semaphore(1)
			self.__ReadCountAccess = Semaphore (1)
			self.__ServiceQueue = Semaphore (1)
			self.__readCount=0
            
	def Writer(self, data):
			with self.__ServiceQueue :
						self.__RessourceAccess.acquire()
			self.extend(data)
			self.__RessourceAccess.release()
			
                
	def extend(self,data):
				Next=self.__head+len(data)
				if (Next == self.__length):
						self.__flag="done"
						return -1
				data_index=(self.__head+np.arange(len(data)))
				self.__data[data_index]=data
				self.__head=Next
				return 0
				
	def Reader(self):
				self.__ServiceQueue.acquire()
				with self.__ReadCountAccess :
						if (self.__readCount ==0) :
								self.__RessourceAccess.acquire()
						self.__readCount+=1
						self.__ServiceQueue.release()
				data=self.get()
				with self.__ReadCountAccess :
						self.__readCount-=1
						if (self.__readCount ==0):
								self.__RessourceAccess.release()
				return data			
        
	def get(self):
					
					if self.__tail >= self.__lengthMax:
							self.__tail=self.__lengthMax
					idx=(0+np.arange(self.__tail))
					temp=np.array(self.__data[idx])
					MFCCs=temp.reshape((len(idx)/13),13).T
					delta=function.deltaMFCCs(MFCCs,9)
					deltaDelta=function.deltaMFCCs(delta,9)
					mfccs=np.concatenate((MFCCs,delta,deltaDelta),axis=0)
					mfccs_reshape=mfccs.reshape(mfccs.size,order='F')
					self.__data=np.zeros(2600)
					self.__head=0
					self.__tail=0
					self.__out="out"
					return np.concatenate((mfccs_reshape,np.zeros(self.__lengthMax*3-mfccs_reshape.size)),axis=0)#,self.__SampleRingBuffer.getSegments(len(idx)/13)

	def flag(self,data,threshold,entropyDistance,entropyThresh,coeff,energy, AudioSample):
                # first case
					if self.__head==self.__length:
									self.__flag="done"
					if (data<threshold or entropyDistance<entropyThresh)  and self.__flag=="rejeted" :
									self.__flag="out"
                        
					if  self.__flag=="admit" :
									self.__flag="out"
                        
					if (data>=threshold and entropyDistance>=entropyThresh) and self.__flag=="out" :
								self.__flag="in"
							#	self.__SampleRingBuffer.initialize()
								self.__Env.initialize()
                        
					if (data<threshold and entropyDistance<entropyThresh) and self.__flag=="in" :
								self.__flag="io"
	
					if (data>=threshold and entropyDistance>=entropyThresh) and self.__flag=="io" :
							self.__flag="in"

					if self.__flag=="in" or self.__flag=="io" :
							self.__EnergyCoeffArray[0]=energy
							self.__EnergyCoeffArray[1+np.arange(12)]=coeff[1+np.arange(12)]
                        
                        
					if self.__flag=="in" :
							
							self.__tail=self.__head
							self.Writer(self.__EnergyCoeffArray)
							#self.__SampleRingBuffer.extendSegments(AudioSample)
							self.__count=0
							self.__envelope = self.__Env.limit(AudioSample)
							
					if self.__flag=="io" :
							current_Env=self.__Env.limit(AudioSample)
							self.__tail =DSP.EndSegments(self.__envelope, current_Env,self.__head,self.__tail)
							self.__envelope=current_Env
						
							if self.__count <=self.__numberOfWindowRejection :
									self.__count+=1
									self.Writer( self.__EnergyCoeffArray)
									#self.__SampleRingBuffer.extendSegments(AudioSample)
							else :
									delete_index=(self.__tail+np.arange(self.__head-self.__tail))
									self.__data[delete_index]=0.
									self.__count=0
                           #    	 print(self.__index)
									self.__flag="done"
									self.__head=0

					if self.__flag=="done" :
							if self.__tail< self.__lengthOfWindowMinima :
									self.__flag="rejeted"
									#print "rejected"
									self.__data=np.zeros(2600)
									self.__head=0
							else :
									self.__flag="admit"
									#print "tail was :", self.__tail

					return self.__flag


                                
                
