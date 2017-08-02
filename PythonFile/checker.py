from __future__ import division
import numpy as np
import numpy.matlib
import tools
import math
import struct
import array
import tools
from sklearn.cluster import KMeans
import os
import AudioIO
import MachineLearning
import Sphere
import sys
# spherical k-means
from spherecluster import SphericalKMeans
from spherecluster import VonMisesFisherMixture
import Sphere2 
# PSO

import random
import math
from Swarm import Swarm
import FitnessFunction
import numpy as np

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-07-21"
__version__="1.0-dev"


def ImportData(path):
				# go in DataBase folder 
				os.chdir(path)
				
				# Check folder in this directory
				listdirectory = os.listdir(".")
				# memory allocation
				Features=np.array([]).reshape(4680,0)
				ClassNormal=np.array([]).reshape(1,0)
				print tools.bcolors.OKBLUE +"Reading Data"+ tools.bcolors.ENDC
				# read loop
				i=0
				for filename in listdirectory :
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=100)
						if AudioIO.FolderClassDictionnary2(filename)>0 : 
								os.chdir(filename)
								listoffile=os.listdir(".")
								
								for allfile in listoffile :
											data=(np.loadtxt(allfile)).reshape(4680,1)
											Features=np.hstack([Features,data])
								classNormal=np.matlib.repmat(AudioIO.FolderClassDictionnary2(filename),1,len(listoffile))
								ClassNormal=np.hstack([ClassNormal,classNormal])
								os.chdir('../')
						i+=1
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=100)
				os.chdir('../')
				# return 
				np.savetxt('b.out', ClassNormal[0])
				return Features, ClassNormal[0]

def Angle2RotationMatrix(Theta,Phi):
			
				#define new vector director
				u=np.zeros((3),'f')
				u[0]=-math.sin(math.radians(Theta))
				u[1]=math.cos(math.radians(Theta))
				
				# some angles
				cosPhi=math.cos(math.radians(Phi))
				sinPhi=math.sin(math.radians(Phi))
				
				# Phi Rotation
				RotationPhi=np.zeros((3,3),'f')
				RotationPhi[0,0]=(u[0]**2)*(1-cosPhi)+cosPhi#u[0]**2+(1-u[0]**2)*cosPhi
				RotationPhi[0,1]=u[0]*u[1]*(1-cosPhi)
				RotationPhi[0,2]=-u[1]*sinPhi
				RotationPhi[1,0]=u[0]*u[1]*(1-cosPhi)
				RotationPhi[1,1]=(u[1]**2)*(1-cosPhi)+cosPhi
				RotationPhi[1,2]=u[0]*sinPhi
				RotationPhi[2,0]=u[1]*sinPhi
				RotationPhi[2,1]=-u[0]*sinPhi
				RotationPhi[2,2]=cosPhi
				# Theta Rotation
				RotationTheta=np.zeros((3,3),'f')
				RotationTheta[0,0]=u[1]
				RotationTheta[0,1]=-u[0]
				RotationTheta[0,2]=0
				RotationTheta[1,0]=-u[0]
				RotationTheta[1,1]=u[1]
				RotationTheta[1,2]=0
				RotationTheta[2,0]=0
				RotationTheta[2,1]=0
				RotationTheta[2,2]=1
				
				RotationMatrix=RotationTheta.dot(RotationPhi)
				return RotationMatrix


class Calculation(object):
		def __init__(self,path, file_load):
			self.__svm=AudioIO.LoadClassifier("SVM_Trained")
			self.__svmL=AudioIO.LoadClassifier("LeftSVM_Trained")
			self.__svmR=AudioIO.LoadClassifier("RightSVM_Trained")
			self.__F,self.__C=ImportData(path)
			self.__Sph_Cal=Sphere2.Sphere_calibration()
			self.__x=np.array([0.,0.,0.,0.,0.,0.])#np.loadtxt(file_load)
			
		def Score(self,best_score):
				local_score=0.0
				for l in range(12):
						local_score+=best_score[l]
				local_score=local_score/12
				return local_score
						
				
		def InvertClass(self,Label):
                    return { 
						1 : 0,
						2 : 1,
						3 : 2,
						4 : 3,
						5 : 4,
						6 : 5,
						7 : 6,
						8 : 7,
						9 : 8,
						10 : 9,
						11 : 10,
                        12 : 11,
                            }.get(Label,0)
                            
		def CompileSVMChecking(self,features,Class):
				best_score=np.zeros((12),'f')
				test_score=np.zeros((12),'i')
				ligne,column=features.shape
				for i in range(column):
						classL=int( MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR,features[:,i].reshape(1,-1))[1][0])
						Label=AudioIO.InvertClass(classL)
						if Label == Class[i]:
								best_score[self.InvertClass(Class[i])]+=1
						test_score[self.InvertClass(Class[i])]+=1
				if np.sum(test_score)!=len(Class):
						print "Error"
				for i in range(12):
						best_score[i]=best_score[i]/test_score[i]
				return best_score
	
	
		def func1(self):
			featuresSphere=np.array([]).reshape(4680,0)
			RotationMatrix=Angle2RotationMatrix(0.,0.)#(self.__x[6],self.__x[7])
			RotationMatrix_e=Angle2RotationMatrix(0.,0.)#(self.__x[8],self.__x[9])
			mean_d=0#[self.__x[10],self.__x[11],self.__x[12]]
			mean_e=0#[self.__x[13],self.__x[14],self.__x[15]]
			std_d=0#[self.__x[16],self.__x[17],self.__x[18]]
			std_e=0#[self.__x[19],self.__x[20],self.__x[21]]
			center=np.zeros((6),'f')
			for i in range (len(center)) :
				center[i]=self.__x[i]
			for l in range (self.__F.shape[1]):
				featuresSphere=np.hstack([featuresSphere,self.__Sph_Cal.DoubleSphere2(self.__F[:,l],"test",center,RotationMatrix,RotationMatrix_e,mean_d,mean_e,std_d,std_e).reshape(4680,1)])
			curr_score=self.CompileSVMChecking(featuresSphere, self.__C)	
			#print curr_score
			score= self.Score(curr_score)
			return score
			

checking=Calculation("Jean-Michel","Value_Test.out")
score=checking.func1()
print score



