# all import here
import alsaaudio as alsa
from multiprocessing import Process, Queue , Pool , Lock
import numpy as np
import math
import struct
import array
import time
import DSP
import wave
import os
from threading import Thread
import RingBuffer
import spectral_entropy
import function
import mfccbuffer
import MFCC
from collections import deque
from scipy.signal import hilbert
import AudioIO
import tools
__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-14"
__version__="1.1-dev"

class Record(object) :
		"""Initialize audio buffer"""
		def __init__(self):
        # all queues
			self.__read_queue = Queue()
			self.__read_frame = Queue()
			self.__write_queue=Queue()
			#self.__RingBufferWrite_queue=Queue()
			#self.__RingBufferRead_queue=Queue()
	# params  
			self.__format=alsa.PCM_FORMAT_S16_LE # format of sample 
			self.__byte =4 # size of each sample 
			self.__rate=8000 # sample rate
			self.__channels=1 # number of channel use in record
			self.__max=48000 # length max of ring buffer for float values
	# change some parameters in terms of sample rate 
			if self.__format==alsa.PCM_FORMAT_S16_LE :
				self.__mgax=self.__max/2
				self.__byte=self.__byte/2
				self.__push_value=[self.__max/3, 2*self.__max/3,self.__max]
       # self.__raw_data=[None for i in xrange(self.__max)]





        #### NO PCM-NONBLOCK ELSE ERROR NO THE SAME CADENCE BETWEEN PROCESSES ####
		""""Reads audio from ALSA audio device """
		def __read(self) :
			card='sysdefault:CARD=Device'  # define default recording card 
			inp = alsa.PCM(alsa.PCM_CAPTURE, alsa.PCM_NORMAL,card) 
			inp.setchannels(1) # number of channels
			inp.setrate(self.__rate) # sample  rate
			inp.setformat(self.__format) # format of sample
			inp.setperiodsize(self.__rate / 50) # buffer period size
			print tools.bcolors.OKGREEN + "In alsa_record - Audio Device is correctly parameted" + tools.bcolors.ENDC
        

			while True :
					frame_count, data = inp.read()  # process to get all value from alsa buffer -> period size * bytes per sample
					self.__read_queue.put(data) # put data in queue -> string type
					self.__read_frame.put(frame_count) # put length -> over 0 data else None


		def __write(self):
				card='sysdefault:CARD=Device'

				outp = alsa.PCM(alsa.PCM_PLAYBACK, alsa.PCM_NORMAL,card)
				outp.setchannels(1)
				outp.setrate(self.__rate)
				outp.setformat(alsa.PCM_FORMAT_S16_LE)
				outp.setperiodsize(self.__rate / 50)

				while True:

					data = self.__write_queue.get()

					outp.write(data)




		def __pre_post_data(self):
				zeros = np.zeros(self.__rate / 50, dtype = np.int16)

				for i in range(0, gself.__byte):
					self.__write_queue.put(zeros)


            

		""" Run proccesses """
		def run(self):
        #self.__pre_post_data()
       # index=Queue()
				self.__read_process = Process(target=self.__read)
				self.__write_process = Process(target = self.__write)
				self.__read_process.start()
				self.__write_process.start()
      
		def runBuffer(self):
				print tools.bcolors.WARNING + "Data Collector is running" + tools.bcolors.ENDC
				RingLength=24650
				window_sample=200
				step_sample=80
				self.__RingBufferWrite_queue=Queue()
				self.__RingBufferRead_queue=Queue()
				ring=RingBuffer.RingBuffer(RingLength,window_sample,step_sample)
				self.__RingBuffer_write_process = Process (target =self.__RingBufferWrite, args=(ring,))
				self.__RingBuffer_write_process.start()
		def stop(self):
				self.__read_process.terminate()
				#self.__write_process.terminate()

		def StopBuffer(self):
				print tools.bcolors.WARNING + "Data Collector is stopped" + tools.bcolors.ENDC
				while not self.__RingBufferWrite_queue.empty():
					self.__RingBufferWrite_queue.get()
				while not self.__RingBufferRead_queue.empty():
					self.__RingBufferRead_queue.get()
				self.__RingBuffer_write_process.terminate()
        
		def read(self):
				return self.__read_queue.get() , self.__read_frame.get()     

		def write(self, data):
				self.__write_queue.put(data)



    # Pseudonymize the audio samples from a binary string into an array of integers
		def pseudonymize(self, s):

				sl=len(s)/self.__byte
				return struct.unpack('<%dh' % sl,s)
    #np.fromstring(s[:2*8000], dtype=np.uint16)

		def depseudonymize(self, a):
				s = ""
				for elem in a:
					s += struct.pack('h', elem)
				return s

		"""  Ring Buffer -> READ AND WRITE METHODS """
		def __RingBufferWrite(self,ring):
				flag=0
				temp=np.zeros(400)
				while True :
					data=self.__RingBufferWrite_queue.get()
					ring.extend(data)
					if flag==2 :
						for i in range(0,2):
							temp.append(ring.get().tolist())
					else :
						flag+=1
						temp=0.01*np.ones((2,200))
							
					self.__RingBufferRead_queue.put(temp)
					temp=[]


		def RingBufferWrite(self,data):
				self.__RingBufferWrite_queue.put(data)
        
		def __RingBufferRead(self,ring):
				flag=0
				while True :
					if flag==0:
						temp=0
						flag=1
					else :
						temp=ring.get()
					self.__RingBufferRead_queue.put(temp)

		def RingBufferRead(self):
				return self.__RingBufferRead_queue.get()
    
		 



if __name__=='__main__' :
    audio= Record()
    mfcc = MFCC.MFCCs()
    entropy = spectral_entropy.SPECTRAL_ENTROPY()
    buff=mfccbuffer.MFFCsRingBuffer()
    RingLength=24650
    window_sample=200
    step_sample=80

   # store=RingBuffer.WaitingBuffer(10,window_sample)
    audio.run()
    cur=0
    tail=0

    i=0 
    c=[[],[]]
    j=0
    fl="out"
    count=0
    c=[] 
    coeff=np.empty(13,'f')
    energy=np.zeros(1)

    # mfcc
    mfccN=np.zeros(13)
    mfccNoise=np.zeros(13)
    mfc=np.empty((26,200),'f')
    # entropy
    SEntropy=np.zeros(13)

    entropyNoise=0
    entropyDistance =0
    entropyN=0
         # threshold

    entropyData =deque([])
    entropyThreshNoise=0
    entropyThresh = 0
    #audio 
    audioData=[]
    s=0
    th=[[],[]]
    endpoint=np.empty(2,'f')
    corr=np.empty((2,1),'f')
    flag=0
    while True :
        data, length = audio.read()
        pdata=audio.pseudonymize(data)

        ndata=DSP.normalize(pdata,32767.0)
        audio.RingBufferWrite(ndata)
        if (c==[]) :
            c=audio.RingBufferRead()
        else :
            print ("Overwrite")
            break
        if flag < 3:
            flag+=1

        else :
            for i in range(0,2) :

                # return MFCC and spectral entropy
                coeff,energy=mfcc.MFCC(np.array(c[i]))
                SEntropy=entropy.SpectralEntropy(np.array(c[i]))
                if j<20 :
                    mfccNoise+=np.array(coeff)
                    entropyData.append(SEntropy)
                    j+=1
                    if j==20 :
                        mfccNoise=mfccNoise/20
                        entropyNoise = np.mean(entropyData)
                        Data=entropyData
                        entropyData=deque([])
                        for k in range(0,len(Data)) :
                            entropyData.append(function.distance(Data[k],entropyNoise))
                        entropyThreshNoise =function.MeanStandardDeviation(entropyData,3)
                else :
                    # return MFCC and Spectral Entropy background noise
                    mfccN=function.updateMFCCsNoise(np.array(coeff),mfccNoise, 0.90)
                    entropyN=function.updateEntropyNoise(SEntropy,entropyNoise, 0.95)
                    
                    # return correlation and distance of MFCC and Entropy
                    corr=function.correlation_1D(np.array(coeff),mfccN)
                    entropyDistance=function.distance(SEntropy,entropyN)
                    
                    # rotate value in entropyData bufferT
                    entropyData.rotate(-1)
                    entropyData[19]=entropyDistance
                    
                    # update threshold 
                    th[i]=function.sigmoid(10,5,corr)
                    entropyThresh=function.EntropyThresholdUpdate(entropyData, entropyThreshNoise,0.96)
                    
                   # print(entropyThreshNoise)
                    if entropyDistance >=  entropyThreshNoise:
                        print "dist" , entropyDistance , "th" , entropyThresh

                     # flag
                    fl=buff.flag(corr,th[i],entropyDistance,entropyThresh,coeff,energy,np.array(c[i]))
                    if fl=="admit" :

                        mfc,audioData=buff.get()
                    ### playback
                        np.savetxt('coeff.out',mfc)
                    #    np.savetxt('data.out',audioData)
                      #  np.savetxt('coeff2.out', AudioIO.Subframe(audioData))
                       # file=wave.open('test.wav','wb')
                       # file.setparams((1,2,8000,len(audioData),"NONE","not compressed"))
                       # file.writeframes(audio.depseudonymize(DSP.denormalize(audioData,32768.)))
                     #   file.close()
                    #### end of playback
                        print("  #############################")
        print "flag is : " , fl
        c=[]
       # ndata=DSP.denormalize(pdata,0xFF)
        ndata=audio.depseudonymize(pdata)
        audio.write(ndata)
#
    print("out of loop")
    print("end of transmission -> waiting new data")
