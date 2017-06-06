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
from threading import Thread
import alsaaudio as alsa
import struct

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-14"
__version__="1.0-dev"

# RING BUFFER #
class RingBuffer(object):

		"""  Initialize ring buffer """
		def __init__(self,length,window_sample,step_sample):
			self.__data=np.zeros(length)
			self.__index=0
			self.__head=0
			self.__length=length
			self.__window=window_sample
			self.__step=step_sample
			self.__shift=0 # index for get
			self.__clean=0
			self.__offsetIndex=((window_sample-step_sample)+np.arange(step_sample))
			self.__lock=Lock()
			self.__queue=Queue()
        
		""" Add data to the ring buffer -> data is anarray of float I suppose """
		def extend(self,queue):
			while True :
				data=np.array(self.__queue.get())
				self.__lock.acquire()
				print "write lock"
				data_index=(self.__index + np.arange(data.size))
				if np.all(self.__data[data_index]==np.zeros(len(data_index))) :
					self.__data[data_index]=data
					self.__index=data_index[-1]+1
					self.__index=self.__index%self.__length
				else :
					print("Error : RingBuffer is overwritten ")
				self.__lock.release()
				print "write unlock"
		
		def get(self,queue):
			while True :
				time.sleep(0.05)
				if (self.__index>=self.__shift+200):
					print self.__index , "\n"
				#	self.__lock.acquire()
					print "read lock"
					idx=(self.__shift + np.arange(self.__window))
					idx_clean=(self.__clean + np.arange(self.__step))
					if self.__shift+self.__window > self.__length :
							temp_end=(np.arange(self.__shift,self.__length))
							temp_beg=(0+np.arange(self.__window-temp_end.size))
							idx= np.concatenate([temp_end,temp_beg])
					if self.__clean+self.__step > self.__length :
							clean_end=(np.arange(self.__clean,self.__length))
							clean_beg=(0+np.arange(self.__step-clean_end.size))
							idx_clean= np.concatenate([clean_end,clean_beg])
					self.__shift+=self.__step
					self.__clean+=self.__step
					if self.__shift >= self.__length :
							self.__shift=self.__shift-self.__length
					if self.__clean >= self.__length :
						self.__clean=self.__clean-self.__length
					temp=self.__data[idx]
					self.__data[idx_clean]=np.zeros(self.__step)
				#	self.__lock.release()
					print "read unlock"
					queue.put(temp)
		#return temp
		def _pp(self, queue):
			while True :
				a= queue.get()

		def readUSB(self) :
			card='sysdefault:CARD=Device'  # define default recording card 
			inp = alsa.PCM(alsa.PCM_CAPTURE, alsa.PCM_NORMAL,card) 
			inp.setchannels(1) # number of channels
			inp.setrate(8000) # sample  rate
			inp.setformat(alsa.PCM_FORMAT_S16_LE) # format of sample
			inp.setperiodsize(8000 / 50) # buffer period size
			print  "In alsa_record - Audio Device is correctly parameted" 
			while True :
					frame_count, data = inp.read()
					self.__queue.put(self.pseudonymize(data))


		def pseudonymize(self, s):
				sl=len(s)/2
				return struct.unpack('<%dh' % sl,s)
	
		def run(self):
       # index=Queue()
				self.__read_process = Process(target=self.readUSB)
				#self.__write_process = Process(target = self.__write)
				self.__read_process.start()
					
if __name__=='__main__' :
	a=np.ones(170)*0.1
	Buff=RingBuffer(24650,200,80)
	Buff.run()
	data= Queue()
	inputD=Queue()
		
	readL=Thread(target=Buff.get,args=(data,))
	writeL=Thread(target=Buff.extend,args=(inputD,))
	printd=Thread(target=Buff._pp,args=(data,))
	readL.start()
	writeL.start()
	printd.start()
		
