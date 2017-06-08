# all import here
import alsaaudio as alsa
from multiprocessing import Process, Queue , Lock
import numpy as np
import math
import struct
import array
import time
import DSP
import wave
import os
from threading import Thread , Semaphore
import alsaaudio as alsa
import struct
import DSP
import Limiter

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-06-07"
__version__="1.0-dev"

# RING BUFFER #
class RingBuffer(object):

		"""  Initialize ring buffer """
		def __init__(self,length,window_sample,step_sample):
				self.__tail=0
				self.__head=0
				self.__flag=0
				self.__MaxLen=length
				self.__data=np.zeros(length)
				self.__window=window_sample
				self.__step=step_sample
				
				## semaphore & Lock
				self.__RessourceAccess= Semaphore(1)
				self.__ReadCountAccess = Semaphore (1)
				self.__ServiceQueue = Semaphore (1)
				self.__readCount=0
				
				## Queue
				self.__ReadQueue= Queue()
				self.__USBData = Queue()
				
		def Writer(self,data):
				with self.__ServiceQueue :
						self.__RessourceAccess.acquire()
				#print "Write" 
				self.IsFull_Write(data)
				self.__RessourceAccess.release()
			
			
		def IsFull_Write(self,data):
				Next=self.__head+len(data)
				if (Next >= self.__MaxLen):
						Next =0
						self.__flag=1
				if ( Next == self.__tail):
						print " ##### Overwrite #####" , self.__tail , self.__head
						return -1
				data_index=(self.__head + np.arange(len(data)))
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
				#print "Read"
				self.IsEmpty_Read()
				with self.__ReadCountAccess :
						self.__readCount-=1
						if (self.__readCount ==0):
								self.__RessourceAccess.release()
		def IsEmpty_Read(self):
			#	print self.__head , self.__tail 
				if (self.__head == self.__tail):
						#print "No Data"
						return -1
				Next=self.__tail+self.__window
				if ( Next >= self.__MaxLen):
						Next = Next-self.__MaxLen
						self.__flag=0
				if (Next >= self.__head and self.__flag ==0):
						return -1
				if (Next <= self.__head and self.__flag ==1):
						return -1
				#print self.__head , self.__tail , Next
				idx=(self.__tail + np.arange(self.__window))
				if self.__tail+self.__window >= self.__MaxLen :
							temp_end=(np.arange(self.__tail,self.__MaxLen))
							temp_beg=(0+np.arange(self.__window-temp_end.size))
							idx= np.concatenate([temp_end,temp_beg])
				self.__ReadQueue.put(self.__data[idx])
				self.__tail+=self.__step
				if (self.__tail >= self.__MaxLen ):
						self.__tail = self.__tail - self.__MaxLen
				return 0



		def __readUSB(self) :
				card='sysdefault:CARD=Device'  # define default recording card 
				inp = alsa.PCM(alsa.PCM_CAPTURE, alsa.PCM_NORMAL,card) 
				inp.setchannels(1) # number of channels
				inp.setrate(8000) # sample  rate
				inp.setformat(alsa.PCM_FORMAT_S16_LE) # format of sample
				inp.setperiodsize(8000 / 50) # buffer period size
				print  "In alsa_record - Audio Device is correctly parameted" 
				Compressor=Limiter._Limiter()
				while True :
						frame_count, data = inp.read()
						if frame_count :
							self.__USBData.put(Compressor.arctan_compressor(DSP.normalize(self.pseudonymize(data), 32768.0)))

		def readUSB(self):
				return self.__USBData.get()

		def pseudonymize(self, s):
				sl=len(s)/2
				return struct.unpack('<%dh' % sl,s)
	
		def run(self):
				self.__read_process = Process(target=self.__readUSB)
				self.__read_process.start()
		
		
		## test 
		def Recorder(self):
				self.run()
				while True :
						data=self.readUSB()
						self.Writer(data)
			
		def Treatment(self):
				
				while (self.__ReadQueue.empty()):
						self.Reader()
				a= self.__ReadQueue.get()
				return a
			
					
if __name__=='__main__' :
			Ring =RingBuffer(24650,200,80)
			Ring.run()
			write=Thread(target=Ring.Recorder)
			read=Thread(target=Ring.Traitment)
			write.start()
			read.start()
			
