""" An audio Limiter to control input gain and avoid saturation """
from numpy import max, abs , zeros 
import numpy as np
import math
import struct
import array
""" Inspired on the work of """
__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-05-30"
__version__="1.0-dev"


class _Limiter(object):
	def __init__(self):
		self.__attack=0.9
		self.__release=0.999
		self.__gain=1
		self.__delay=40
		self.__delayLine=np.zeros(self.__delay, 'f')
		self.__enveloppe=0
		self.__delayIndex=0
		self.__threshold=0.8
	
	def limit(self,signal):
				for i in range (len(signal)):
					self.__delayLine[self.__delayIndex]=signal[i]
					self.__delayIndex=(self.__delayIndex+1)%self.__delay
					
					self.__enveloppe*=self.__release 
					self.__enveloppe=max(abs(signal[i]),self.__enveloppe)
					
					if self.__enveloppe > self.__threshold :
						gain=(1+self.__threshold-self.__enveloppe)
					else :
						gain= 1.0
					
					self.__gain=(self.__gain*self.__attack + gain*(1-self.__attack))
					
					signal[i]=self.__delayLine[self.__delayIndex]*self.__gain
		
				return signal
			
	def clearInit(self):
		self.__attack=0.9
		self.__release=0.999
		self.__gain=1
		self.__delay=40
		self.__delayLine=np.zeros(self.__delay, 'f')
		self.__enveloppe=0
		self.__delayIndex=0
		self.__threshold=0.8
	
