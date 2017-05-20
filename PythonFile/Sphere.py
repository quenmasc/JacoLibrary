import numpy as np
import numpy.matlib
import tools
import math
import struct
import array
import time

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-14"
__version__="1.1-dev"

class Sphere_calibration(object):
	def __init__(self):
		self.__rayon=1
		self.__center=np.array([0,0,0])
	
	def Length(self, features):
		self.__DataLength=180 #features.shape[0]
		self.__feature=np.zeros((39,180*150))
		self.__Output=np.zeros(180*1950) # 13 * 150
		#return DataLength , feature, Output
		
	def ClassAndFeaturesSplit(self, features, label):
		self.Length(features)
		for i in range(0,self.__DataLength):
			idx=(i*150+np.arange(150))
			idx_2=(i*1950+np.arange(1950))
			self.__feature[:,idx]=np.reshape(features,(39,150), order='F')
			self.__Output[idx_2]=numpy.matlib.repmat(label,1,1950)
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
		
		# 0 mean and one std
				## allocation of memory
		new_x=np.zeros(self.__DataLength*150*13)
		new_y=np.zeros(self.__DataLength*150*13)
		new_z=np.zeros(self.__DataLength*150*13)
				## operation
		for i in range(0,x.size):
			if x[i] != 0:
				new_x[i]=((x[i]-meanx)/stdx)-self.__center[0]
				new_y[i]=((y[i]-meany)/stdy)-self.__center[1]
				new_z[i]=((z[i]-meanz)/stdz)-self.__center[2]
			else :
				new_x[i]=0
				new_y[i]=0
				new_z[i]=0
		# Paramter to create sphere with dataset
				## allocation of memory
		P_abs=np.zeros(self.__DataLength*150*13)
				## operation
		P=(np.vstack((new_x,new_y,new_z))).T
		for i in range(0, x.size):
			P_abs[i]=math.sqrt(new_x[i] **2 +new_y[i]**2 + new_z[i]**2)
		Q=(self.__rayon/P_abs).T
		# Sphere data
				## allocation of memory
		SphereData=np.zeros((self.__DataLength*150*13,3))
		for i in range(0,3):
			SphereData[:,i]=Q*P[:,i]
		feat_struct=np.concatenate((SphereData[:,0].reshape(13,150*self.__DataLength,order='F'),SphereData[:,1].reshape(13,150*self.__DataLength,order='F'),SphereData[:,2].reshape(13,150*self.__DataLength,order='F')),axis=0)
		
		# return features matrix
				## allocation of memory
		features=np.zeros((39*150,self.__DataLength))
		for i in range (0,self.__DataLength):
			intermediaire=feat_struct[:,(i*150+np.arange(150))]
			features[:,i]=intermediaire.reshape(intermediaire.size, order='F')
		print(features)
		return features

if __name__ == "__main__" :
	Sphere= Sphere_calibration()
	b=np.ones(5850)
	b[1]=2
	b[16]=100
	b[34]=4582
	b[5823]=18
	Sphere.ClassAndFeaturesSplit(b,1)
