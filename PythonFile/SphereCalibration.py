import numpy as np
import numpy.matlib
import tools
import math
import struct
import array
import time
import cPickle
import tools
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from multiprocessing import Pool
from sklearn.cluster import KMeans
import os
import AudioIO

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-06-16"
__version__="1.0-dev"

class Sphere_Calibrator(object):
		def __init__(self,nWord,CandidateName):
				self.__accuracyResult=np.zeros(nWord)
				self.__nClusters=7
				self.__initCentroid=np.array([[0,0,0],
											  [1,0,0],
											  [0,1,0],
											  [-1,0,0],
											  [0,-1,0],
											  [0,0,1],
											  [0,0,-1]], np.float64)
				
									#np.array([[0,1,0,-1,0,0,0],
									#		  [0,0,1,0,-1,0,0],
									#		  [0,0,0,0,0,1,-1]],np.float64)
				self.__rayon=1.0
				self.__center=np.array([0,0,0])
				self.__Candidate=CandidateName
		
		
		def Sphere(self,features,Label,nClass):
				self.__DataLength=int(features.size/features.shape[0])
				if features.shape[1]==1:
						self.__prof=int((features.size/39))
				else :
						self.__prof=int((features.size/features.shape[1])/39)
				# new features matrix 
				self.__feature=np.zeros((39,self.__DataLength*self.__prof))
				self.__Label=np.zeros((self.__DataLength*self.__prof*13))
				for i in range(0,self.__DataLength):
						idx=(i*self.__prof+np.arange(self.__prof))
						idx_2=(i*self.__prof*13+np.arange(self.__prof*13))
						self.__feature[:,idx]=np.reshape(features[:,i],(39,self.__prof), order='F')
						self.__Label[idx_2]=numpy.matlib.repmat(Label[i],1,self.__prof*13)		
				# reshape all matrix in 3 vector -> MFCC, VMFCC, VVMFCC
				x=self.__feature[(0+np.arange(13)),:].reshape(self.__feature[(0+np.arange(13)),:].size, order='F')
				y=self.__feature[(13+np.arange(13)),:].reshape(self.__feature[(13+np.arange(13)),:].size, order='F')
				z=self.__feature[(26+np.arange(13)),:].reshape(self.__feature[(26+np.arange(13)),:].size, order='F')	
				# mean and std of x, y and z
				meanx=np.mean(x)
				meany=np.mean(y)
				meanz=np.mean(z) 
				stdx=np.std(x)
				stdy=np.std(y)
				stdz=np.std(z)
	
				## allocation of memory
				new_x=np.zeros(self.__DataLength*self.__prof*13)
				new_y=np.zeros(self.__DataLength*self.__prof*13)
				new_z=np.zeros(self.__DataLength*self.__prof*13)
				P_abs=np.zeros(self.__DataLength*self.__prof*13)
				Q=np.zeros(x.size)
				## operation
				for i in range(0,x.size):
						if x[i] != 0:
								new_x[i]=((x[i]-meanx)/stdx)-self.__center[0]
								new_y[i]=((y[i]-meany)/stdy)-self.__center[1]
								new_z[i]=((z[i]-meanz)/stdz)-self.__center[2]
								P_abs[i]=math.sqrt(new_x[i] **2 +new_y[i]**2 + new_z[i]**2)
								Q[i]=(self.__rayon/P_abs[i]).T
						else :
								new_x[i]=0
								new_y[i]=0
								new_z[i]=0
								P_abs[i]=0
								Q[i]=0
				# Paramter to create sphere with dataset
				P=(np.vstack((new_x,new_y,new_z))).T
				
				# Sphere data
				## allocation of memory
				SphereData=np.zeros((self.__DataLength*self.__prof*13,3))
				for i in range(0,3):
						SphereData[:,i]=Q*P[:,i]
						for j in range(0,self.__DataLength*self.__prof*13):
								if math.isnan(SphereData[j,i])==True :
										SphereData[j,i]=0
			
				
				print SphereData.shape
				# KMEANS below
				mu=np.zeros((self.__nClusters,nClass*3),'f')
				print mu.shape
				Theta=np.zeros((nClass,self.__nClusters),'f')
				Phi=np.zeros((nClass,self.__nClusters),'f')
				print "Kmeans calculation in progress"
				tools.printProgressBar(0,nClass,prefix='Progress',suffix='Complete',decimals=1, length=50)
				for i in range(1,nClass+1):
					km=KMeans(n_clusters=self.__nClusters,init=self.__initCentroid,n_init=1).fit(SphereData[self.__Label.T==i,:])
					mu[:,(i-1)*3+np.arange(3)]=km.cluster_centers_
					Angle=self.SphericalAngle(km.cluster_centers_.T)
					Theta[i-1,:]=Angle[0,:]
					Phi[i-1,:]=Angle[1,:]
					tools.printProgressBar(i,nClass,prefix='Progress',suffix='Complete',decimals=1, length=50)
				np.savetxt('a.out',mu.T)
				np.savetxt('phi.out',Phi.T)
				np.savetxt('theta.out',Theta.T)
		
		def SphericalAngle(self,mu):
				print mu.shape
				n=mu.shape[1]
				print n
				X=np.zeros((2,n))
				for i in range(n):
							X[:,i]=self.ReturnAngle(mu[0,i],mu[1,i],mu[2,i])
				return X
		
		def ReturnAngle(self,x,y,z):
				if y==0 and x==0 :
						Theta=0
				else :
						Theta=math.degrees(math.atan2(y,x))
				Phi=math.degrees(math.acos(z))
				X=[Theta,Phi]
				return X
				
		def ImportData(self,path):
				# go in DataBase folder 
				os.chdir(path)
				
				# Check folder in this directory
				listdirectory = os.listdir(".")
				
				# memory allocation
				Features=np.array([]).reshape(4680,0)
				ClassNormal=np.array([]).reshape(1,0)
				print "Reading Data"
				# read loop
				i=0
				for filename in listdirectory :
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=50)
						if AudioIO.FolderClassDictionnary(filename)>0 : 
								os.chdir(filename)
								listoffile=os.listdir(".")
								
								for allfile in listoffile :
											data=(np.loadtxt(allfile)).reshape(4680,1)
											Features=np.hstack([Features,data])
											
								classNormal=np.matlib.repmat(AudioIO.FolderClassDictionnary(filename),1,len(listoffile))
								ClassNormal=np.hstack([ClassNormal,classNormal])
								os.chdir('../')
						i+=1
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=50)
				os.chdir('../')
				# return 
				return Features, ClassNormal[0],12
			
		def main(self):
				DataSetPath="DataBase/"
				F,C,n=self.ImportData(DataSetPath)
				self.Sphere(F,C,n)


if __name__=='__main__' :
		 Calibration=Sphere_Calibrator(7,"Quentin")
		 Calibration.main()

