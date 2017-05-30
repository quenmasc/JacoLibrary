""" An audio denoiser to improve features classification """
from numpy import max, abs , zeros 
import numpy as np
import math
import struct
import array
from numpy.fft import fft , ifft

""" inspired on PEETERS GOEFFROY courses  """

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-05-30"
__version__="1.0-dev"

class Spectral_Substraction(object):
	def __init__(self):
		self.__nfft=256
		self.__win=np.hamming(200)
		
	def STFT(self,data):
		Data_fft=fft(data*self.__win, self.__nfft,axis=0)
		return Data_fft
	
	def ISTFT(self,data):
		s=ifft(data,n=200)
		return s.real
	
	def StoreParameter(self, Noise):
		self.__MeanNoise=np.mean(Noise,axis=0)

	def Substraction(self,Input):
		InFFT=self.STFT(Input)
		H=1-(self.__MeanNoise/np.absolute(InFFT))
		H_m=(H+np.absolute(H))/2
		Out=(self.ISTFT(H_m*InFFT))/self.__win
		return Out
		
	
