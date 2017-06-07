import numpy as np
import numpy.matlib as nm
import time
import math
import numpy.fft
__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-05-02"
__version__="1.0-dev"


def mel(f):
    return 1127. * np.log(1. + f / 700.)

def dtcm(N,M):
    return np.sqrt(2.0/M)*np.cos((nm.repmat((0+np.arange(N)),M,1)).T*nm.repmat(math.pi*((1+np.arange(M))-0.5)/M,N,1))

def cepFilter(N,L):
    return 1+0.5*L*np.sin(math.pi*(0+np.arange(N))/L)

def triangularFilter(nb_filter,freq_response,frequency_limits):
        lowFreq=frequency_limits[0]
        upFreq=frequency_limits[1]

        # linspace of frequencies
        
        Hz=np.linspace(lowFreq,upFreq,freq_response)
        # convert Hz scale to Mel scale
        
        melLow=mel(lowFreq)
        melUp=mel(upFreq)

        # filter cut off
        C=melLow+(0+np.arange(nb_filter+2))*((melUp-melLow)/(nb_filter+1))
        
        # convert C to Hz
        C_Hz=700*np.exp(C/1127)-700
        
        # allocate matrix
        TriBankMatrix=np.zeros((nb_filter,freq_response))
        
        # Loop
        for i in range(0,nb_filter):
            for j in range (0, freq_response) :
                if Hz[j]>=C_Hz[i] and Hz[j] < C_Hz[i+1] :
                    TriBankMatrix[i,j]=(Hz[j]-C_Hz[i])/(C_Hz[i+1]-C_Hz[i])
                if Hz[j]>=C_Hz[i+1] and Hz[j]<=C_Hz[i+2] :
                    TriBankMatrix[i,j]=(C_Hz[i+2]-Hz[j])/(C_Hz[i+2]-C_Hz[i+1])

        return TriBankMatrix

class MFCCs(object):
    def __init__(self):
        self.__nbFilter=20
        self.__freqLimits=[300,3700]
        self.__nbCepstralLifter=22
        self.__nbCepstralCoeff=13
        self.__nfft=256
        self.__freqResponse=self.__nfft/2+1 # 256/2 +1
        self.__FilterBank=triangularFilter(self.__nbFilter,
                    self.__freqResponse, self.__freqLimits)
        self.__dct=dtcm(self.__nbCepstralCoeff,self.__nbFilter)
        self.__LowFilterLift=cepFilter(self.__nbCepstralCoeff,self.__nbCepstralLifter)
        self.__prior=0
        self.__alpha=0.97
        self.__win=np.hamming(200)
        
    def magnitude(self, frame):
			frame =self.pre_emphasis(frame) * self.__win
			fft=numpy.fft.fft(frame, self.__nfft,axis=0)
        # Square of absolute value
			return fft 

    def pre_emphasis(self,frame):
        return np.append(frame[0],frame[1:]-self.__alpha*frame[:-1])
    
    def MFCC(self,frame):
        magnitude=np.absolute(self.magnitude(frame))
        logEnergy=math.log(math.fsum((np.absolute(self.magnitude(frame*32768.0)))**2))
        # filterBannk application to the uniquee part of FFT
        FBA= self.__FilterBank.dot(magnitude[(0+np.arange(self.__nfft/2+1))])
        CepstralCoeff=self.__dct.dot(np.log(FBA))
        LiftCepstralCoeff=np.diag(self.__LowFilterLift).dot(CepstralCoeff)
        return LiftCepstralCoeff,logEnergy
        
    def MFCC2(self, frame):
			magnitude=np.absolute(self.magnitude(frame))
			logEnergy=math.log(math.fsum((np.absolute(self.magnitude(frame*32768.0)))**2))
        # filterBannk application to the uniquee part of FFT
			FBA= self.__FilterBank.dot(magnitude[(0+np.arange(self.__nfft/2+1))])
			CepstralCoeff=self.__dct.dot(np.log(FBA))
			LiftCepstralCoeff=np.diag(self.__LowFilterLift).dot(CepstralCoeff)
			LiftCepstralCoeff[0]=logEnergy
			return LiftCepstralCoeff 
        
        
        
