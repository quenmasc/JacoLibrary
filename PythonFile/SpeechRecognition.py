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
from threading import Event
import MachineLearning
import tools
import os
import time
import errno
import Sphere
import SpectralSubstraction
import math
import wave
import struct
from audioop import ratecv
import ReadWriteRingBuffer

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
			self.__semaphore2=threading.Semaphore(0)
			self.__semaphore2Lock=threading.Semaphore(1)
			self.__semaphore=threading.Semaphore(0)
			self.__semaphoreLock=threading.Semaphore(1)
			#   self.__event=Event()
			self.__lock=Lock()
			self.__lock2 = Lock()
			self.__fifo_name= 'fifo'
			
			## shared constructor
			self.__ReadWrite=ReadWriteRingBuffer.RingBuffer(24650,200,80)
			#self.run()
		def Recorder(self):
			
			## all value 
			StartFlag=0
			StartCount=0
			flag=False
			self.__ReadWrite.run()
			#self.__ReadWrite.Recorder()
			## Thread Launcher
			
			self.__t3=threading.Thread(target=self.VocalActivityDetection)
			self.__t3.start()
			#self.__t1=threading.Thread(target=self.__ReadWrite.Recorder)
			#self.__t1.start()
			self.__t4=threading.Thread(target=self.Train)
			self.__t4.start()
			#self.__t2=threading.Thread(target=self.SVM)
			#self.__t2.start()
			self.__ReadWrite.Recorder()
		
			
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
					self.__semaphore.acquire()
					with self.__lock :
							MfccsCoeffGet=MfccsCoeff
							Audio=Data
					self.__semaphoreLock.release()
					newcoeff=(CoeffSphere.ClassAndFeaturesSplit(MfccsCoeffGet,"test")).T 
					classLab=MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR ,newcoeff)
					classL=int(MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR,newcoeff)[1][0])
					print classLab
					#file=wave.open('test.wav','wb')
					#file.setparams((1,2,8000,len(Audio),"NONE", "not compressed"))
					#file.writeframes(self.depseudonymize(DSP.denormalize(Audio,32768.0)))
					#file.close()
					if classL != 8 :
							self.write_Pipe(classL)
					print "Done ..."
				         
		def write_Pipe(self,classL):
			with open('/home/pi/libkindrv/examples/build/%s' %self.__fifo_name,'wb') as f:
				f.write('{}\n'.format(len(bin(classL)[2:])).encode())
				f.write(bin(classL)[2:])
				f.flush()
                   
 

		def VocalActivityDetection(self):
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
			th=0
			endpoint=np.empty(2,'f')
			corr=np.empty((2,1),'f')
			flag=0
			print tools.bcolors.OKGREEN + " Traitment is loaded " + tools.bcolors.ENDC
			while True :
					c=np.zeros(200)
					c=np.array(self.__ReadWrite.Treatment())
					if np.all(c!=np.zeros(len(c))):
							
							coeff,energy=mfcc.MFCC(np.array((c)))
							SEntropy=entropy.SpectralEntropy(np.array((c)))
							
							if j<100 :
								#Noise=SpectralSub.STFT(c[i])
								mfccNoise+=np.array(coeff)
								entropyData.append(SEntropy)
								#BackgroundNoise.append(Noise)
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
									#SpectralSub.StoreParameter(BackgroundNoise)
							else :
								
							# return MFCC and Spectral Entropy background noise
								mfccN=function.updateMFCCsNoise(coeff,mfccNoise, 0.9)
								entropyN=function.updateEntropyNoise(SEntropy,entropyNoise, 0.95)
						
							# return correlation and distance of MFCC and Entropy
								corr=function.correlation_1D(coeff,mfccN)
								entropyDistance=function.distance(SEntropy,entropyN)
						
							# rotate value in entropyData bufferT
								entropyData.rotate(-1)
								entropyData[19]=entropyDistance
							# update threshold 

								th=function.sigmoid(10,5,corr)
								entropyThreshN=function.EntropyThresholdUpdate(entropyData, entropyThreshNoise,0.96)

								fl=buff.flag(corr,th,entropyDistance,entropyThreshN,coeff,energy,c)
								#print fl
								if fl=="admit" :
										self.__semaphoreLock.acquire()
										with self.__lock :
											MfccsCoeff,Data=buff.get()
										self.__semaphore.release()
						     
    

		def depseudonymize(self, a):
			s = ""
			for elem in a:
				s += struct.pack('h', elem)
			return s
			


		def Train(self):
			global MfccsCoeff
			global Data
			print tools.bcolors.OKBLUE +"Ready for Training "+ tools.bcolors.ENDC
			while True :
						#self.__event.set()
						self.__semaphore.acquire()
						#self.__event.clear()
						with self.__lock :
								coeff=MfccsCoeff
								Audio=Data
						x= int( raw_input("Class of the current word\n"))
						print "Labelclass is :" ,x
						if (x!=0):
								struct='DataBase/%s'%AudioIO.TrainClasse(x)
								if not os.path.exists(struct) :
										os.makedirs(struct)
										print tools.bcolors.OKBLUE +"folder :" ,struct, "has been created" + tools.bcolors.ENDC
								os.chdir(struct)
								listdirectory = os.listdir(".")
								name='%s_%s.txt'%(AudioIO.ClassName(x),len(listdirectory))
								if not os.path.isfile(name):
										file(name,'a').close()
										np.savetxt(name,coeff)
										print tools.bcolors.OKGREEN + "Word %s saved - %s"%(AudioIO.ClassName(x),len(listdirectory))+tools.bcolors.ENDC
								os.chdir('../../')
						else :
							pass
						self.__semaphoreLock.release()
						#fil=wave.open('test.wav','wb')
						#fil.setparams((1,2,8000,len(Audio),"NONE", "not compressed"))
						#fil.writeframes(self.depseudonymize(DSP.denormalize(Audio,32768.0)))
						#fil.close()
    
if __name__=='__main__' :
    print "Running ...."
    speech=Speech_Recognition()
    speech.Recorder()
        
