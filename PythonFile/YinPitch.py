""" A Pitch Estimator based on YIN Pitch """
from numpy import max, abs , zeros 
import numpy as np
import math
import struct
import array
from numpy.fft import fft , ifft
import os
import DSP

""" This code is based on the work of ashokfernandez github code"""
__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-06-22"
__version__="1.0-dev"

class Yin_Pitch(object):
		def __init__(self,threshold):
				self.__rate=8000
				
			
		# step 1 : square difference of the signal zith a shifted version of the same signal 
		def YinDifference(self,data):
				for tau in range(self.__halfBufferSize):
					for i in range(self.__halfBufferSize):
						delta=data[i]-data[i+tau]
						self.__YinBuffer[tau]+=delta*delta
		# step 2 : Calculate the cumulative mean on the normalised difference 
		def YinMean(self):
				CurrentSum=0.0
				self.__YinBuffer[0]=1.0
				for tau in range (1,self.__halfBufferSize):
					CurrentSum+=self.__YinBuffer[tau]
					self.__YinBuffer[tau]*=tau/CurrentSum
					
		# step 3 : find the value over the threshold from last step
		def YinThreshold(self):
				for tau in range (2,self.__halfBufferSize):
					if (self.__YinBuffer[tau]< self.__threshold):
						while (tau+1 < self.__halfBufferSize and self.__YinBuffer[tau+1]<self.__YinBuffer[tau]):
								tau+=1
						self.__probability=1-self.__YinBuffer[tau]
						break 
		
				if (tau==self.__halfBufferSize or self.__YinBuffer[tau]>=self.__threshold):
					tau=-1
					self.__probability=0.0
				return tau 
		
		# step 4 : interpolate the shift value to improve pitch estimation
		def YinInterpolation(self, tauEstimate):
				
				if ( tauEstimate <1):
					x0=tauEstimate
				else :
					x0=tauEstimate-1
				
				if (tauEstimate+1< self.__halfBufferSize):
					x2=tauEstimate+1
				else :
					x2=tauEstimate
				
				#interpolate the shift
				if (x0==tauEstimate):
					if ( self.__YinBuffer[tauEstimate]<=self.__YinBuffer[x2]):
						betterTau=tauEstimate
					else :
						betterTau=x2
				elif ( x2==tauEstimate):
					if ( self.__YinBuffer[tauEstimate]<=self.__YinBuffer[x0]):
						betterTau= tauEstimate
					else :
						betterTau=x0
				else :
					s0=0.0
					s1=0.0
					s2=0.0
					s0=self.__YinBuffer[x0]
					s1=self.__YinBuffer[tauEstimate]
					s2=self.__YinBuffer[x2]
					betterTau=tauEstimate+(s2-s0)/(2*(2*(s1-s2-s0)))
				
				return betterTau
		
		
		def GetPitch(self,data):
				tauEstimate=-1
				pitchInHertz=-1.0
				self.YinDifference(data)
				self.YinMean()
				tauEstimate=self.YinThreshold()
				# improve pitch estimate
				if ( tauEstimate!=-1):
					pitchInHertz=self.__rate/self.YinInterpolation(tauEstimate)
				
				return pitchInHertz
		
		def YinInit(self,buffersize,threshold):
				self.__bufferSize=buffersize
				self.__halfBufferSize=int(self.__bufferSize/2)
				self.__YinBuffer=np.zeros((self.__halfBufferSize),'d')
				self.__probability=0.0 # float probability that pithc found is correct
				self.__threshold=threshold  # allowed uncertainty in the result 
				self.__rate=8000
				
		def main(self):
				bufferLength=100
				pitch=0.0
				listdirectory = os.listdir(".")
				for filename in listdirectory :
					extension=os.path.splitext(filename)[1]
					if extension=='.wav':
						f=open(filename,'rb')
						data=f.read()
						data=np.fromstring(data, np.int16)
						x=np.array(data)
						x=DSP.normalize(x,2**16)
						self.YinInit(bufferLength,0.05)
						pitch=self.GetPitch(x)
						while pitch <10 :
							self.YinInit(bufferLength,0.05)
							pitch=self.GetPitch(x)
							bufferLength+=1
							print bufferLength
						print "Pitch is found to be", pitch , "with a proba of " , self.__probability
				return 0

if __name__=='__main__' :
	Pitch=Yin_Pitch(0.05)
	Pitch.main()
					
					
				
				
