import alsaaudio as alsa
from multiprocessing import Process, Queue , Pool , Lock
import numpy as np
import alsa_record
import AudioIO
import MFCC
import spectral_entropy
import mfccbuffer
from collections import deque
import DSP
import function
import threading
import MachineLearning
import tools
import os
import time
import errno
import Sphere
import Limiter
import SpectralSubstraction
import math
import wave
import struct
__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-05-11"
__version__="1.0-dev"

class Speech_Recognition(object):
		""" Semaphore """
		MfccsCoeff=np.empty((39,150),'f')
		audioData=np.array([])
		AudioData=np.array([])
		Data=np.array([])
		ClassLab=0
		""" Thread """ 
		def __init__(self):
			self.__maxconnections=2
			self.__semaphore=threading.BoundedSemaphore(self.__maxconnections)
			self.__condition=threading.Condition()
			self.__semaphore2=threading.BoundedSemaphore(self.__maxconnections)
			self.__condition2=threading.Condition()
			self.__fifo_name= 'fifo'
           
		def Recorder(self):
			global AudioData 
			audio= alsa_record.Record()
			audio.run()
			Limit=Limiter._Limiter()
			i=0 
			c=[]
			flag=False
			#self.__t2=threading.Thread(target=self.SVM)
			#self.__t3=threading.Thread(target=self.VocalActivityDetection)
			#self.__t2.start()
			#self.__t3.start()
			# StartFlag
			StartFlag=0
			StartCount=0
			while True :
					data, length = audio.read()
					#pdata=audio.pseudonymize(data)
					#ndata=DSP.normalize(pdata,32767.0)
					#detection=Limit.limit(ndata)
					#if (StartCount!=0 and StartCount <=150 and StartFlag==0):
					#	StartCount+=1
					#if (StartFlag==0 and StartCount==0 and StartFlag==0):
					#	audio.runBuffer()
					#	flag=True
					#	StartCount+=1
					#if (StartCount >150 and StartFlag==0):
					#	StartFlag=1
					#	audio.StopBuffer()
					#	flag=False 
					#if (detection==1 and flag==False and StartFlag==1):
					#	audio.runBuffer()
					#	flag=True
					#elif (detection==0 and flag==True and StartFlag==1) :
					#	audio.StopBuffer()
					#	flag=False 
					#if (flag==True):
						
					#	audio.RingBufferWrite(ndata)   # this line reduce rapidity of the program
					#	if (c==[]) :
					#		c=np.array(audio.RingBufferRead())
					#	else :

					#		print ("Overwrite")
					#		return
					
					
					#	self.__condition2.acquire()
					#	self.__semaphore2.acquire()
					#	AudioData=c
					#	self.__semaphore2.release()
					#	self.__condition2.notify()
					#	self.__condition2.release()
					#	c=[]
					#ndata=audio.depseudonymize(pdata)
					audio.write(data)
			print("out of loop")
			print("end of transmission -> wait")
      
		def SVM(self):
			global MfccsCoeff
			global Data
			self.__svm=AudioIO.LoadClassifier("SVM_Trained")
			self.__svmL=AudioIO.LoadClassifier("LeftSVM_Trained")
			self.__svmR=AudioIO.LoadClassifier("RightSVM_Trained")
			CoeffSphere=Sphere.Sphere_calibration();
			try :
				os.remove('/home/pi/libkindrv/examples/build/%s' %self.__fifo_name)
			except :
				print "Pipe already removed"
			try :
				os.mkfifo('/home/pi/libkindrv/examples/build/%s'  %self.__fifo_name)
			except OSError as e :
				if e.errno==errno.EEXIST :
					print("File already exist")
				else :
					raise
			print tools.bcolors.OKGREEN + "In SVM Method - All done" + tools.bcolors.ENDC
		
        
        
			while True :
						self.__condition.acquire()
						self.__condition.wait()
						self.__semaphore.acquire()
						MfccsCoeffGet=MfccsCoeff
						Audio=Data
						self.__semaphore.release()
						self.__condition.release()
						newcoeff=(CoeffSphere.ClassAndFeaturesSplit(MfccsCoeffGet,"test")).T
						classLab=MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR ,newcoeff)
						classL=int(MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR,newcoeff)[1][0])
						print classLab
						self.write_Pipe(classL)
						file=wave.open('test.wav','wb')
						file.setparams((1,2,8000,len(AudioData),"NONE","not compressed"))
						file.writeframes(self.depseudonymize(np.array(DSP.denormalize(Audio,32767.)).astype(int)))
						file.close()
						print "Done ..."
				         
		def write_Pipe(self,classL):
			with open('/home/pi/libkindrv/examples/build/%s' %self.__fifo_name,'wb') as f:
				f.write('{}\n'.format(len(bin(classL)[2:])).encode())
				f.write(bin(classL)[2:])
				f.flush()
                   
		def stop(self):
			self.__t1.join()
			self.__t2.join()
        
		def running(self):
			self.__t1=threading.Thread(target=self.Recorder) 
			#self.__t2=threading.Thread(target=self.SVM)
			#self.__t3=threading.Thread(target=self.VocalActivityDetection)
			self.__t1.start()
			#self.__t2.start()
			#self.__t3.start()
			self.__t1.join()
			#self.__t2.join()
			#self.__t3.join()     

		def VocalActivityDetection(self):
			global AudioData
			global MfccsCoeff
			global Data
			mfcc = MFCC.MFCCs()
			entropy = spectral_entropy.SPECTRAL_ENTROPY()
			buff=mfccbuffer.MFFCsRingBuffer()
			SpectralSub=SpectralSubstraction.Spectral_Substraction()
			j=0
			fl="out"
			count=0
			coeff=np.empty(13,'f')
			energy=np.zeros(1)

			# mfcc
			mfccN=np.zeros(13)
			mfccNoise=np.zeros(13)
			# entropy
			SEntropy=np.zeros(13)

			entropyNoise=0
			entropyDistance =0
			entropyN=0
			# threshold

			entropyData =deque([])

			entropyThreshNoise=0l
			entropyThresh = 0
			### spectral substraction 
			BackgroundNoise=deque([])
			#audio 
			audioData=[]
			s=0
			th=[[],[]]
			endpoint=np.empty(2,'f')
			corr=np.empty((2,1),'f')
			flag=0
			while True :
				self.__condition2.acquire()
				self.__condition2.wait()
				self.__semaphore2.acquire()
				c=AudioData
				self.__semaphore2.release()
				self.__condition2.release()
				if flag < 2:
						flag+=1

				else :
						#pool = Pool(processes=2)
						for i in range(0,2) :
							# return MFCC and spectral entropy
							
							
							### allow to delete this line  -- TEST TEST --- ####
							if j>=100:
								d=SpectralSub.Substraction(c[i])
								for k in range (len(d)):
									if math.isnan(d[k])==True :
										c[i,k]=c[i,k]
							 ### end of delete lines 
							 
							 
							coeff,energy=mfcc.MFCC(np.array((c[i])))
							SEntropy=entropy.SpectralEntropy(np.array((c[i])))
							
							if j<100 :
								Noise=SpectralSub.STFT(c[i])
								mfccNoise+=np.array(coeff)
								entropyData.append(SEntropy)
								BackgroundNoise.append(Noise)
								j+=1
								if j==100 :
									mfccNoise=mfccNoise/100
									entropyNoise = np.mean(entropyData)
									Data=entropyData
									entropyData=deque([])
									for k in range(0,len(Data)) :
										entropyData.append(function.distance(Data[k],entropyNoise))
									entropyThreshNoise =function.MeanStandardDeviation(entropyData,3)
									print tools.bcolors.OKBLUE + "Recording is now allowed" +tools.bcolors.ENDC
									n=deque([])
									for i in range(0,20):
										n.append(entropyData[79+i])
									entropyData=deque([])
									entropyData=n
									SpectralSub.StoreParameter(BackgroundNoise)
							else :
								
							# return MFCC and Spectral Entropy background noise
								mfccN=function.updateMFCCsNoise(np.array(coeff),mfccNoise, 0.95)
								entropyN=function.updateEntropyNoise(SEntropy,entropyNoise, 0.9)
						
							# return correlation and distance of MFCC and Entropy
								corr=function.correlation_1D(np.array(coeff),mfccN)
								entropyDistance=function.distance(SEntropy,entropyN)
						
							# rotate value in entropyData bufferT
								entropyData.rotate(-1)
								entropyData[19]=entropyDistance
							# update threshold 

								th[i]=function.sigmoid(10,5,corr)
								entropyThresh=function.EntropyThresholdUpdate(entropyData, entropyThreshNoise,0.95)

								fl=buff.flag(corr,th[i],entropyDistance,entropyThresh,coeff,energy,np.array(c[i]))
								if fl=="admit" :
									self.__semaphore.acquire()
									self.__condition.acquire()
									MfccsCoeff,Data=buff.get()
									self.__condition.notify()
									self.__condition.release()
									self.__semaphore.release()
						#pool.close()			

				c=[]     
    

		def depseudonymize(self, a):
			s = ""
			for elem in a:
				s += struct.pack('h', elem)
			return s
    
if __name__=='__main__' :
    print "Running ...."
    speech=Speech_Recognition()
    speech.running()
        
