import numpy as np
import numpy.matlib
import tools
import math
import struct
import array
import time
import tools
import cPickle
 

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-07-09"
__version__="1.0-dev"

class Sphere_calibration(object):
	def __init__(self):
		self.__rayon=1
		self.__center=np.array([0,0,0])
	
	def Length(self, features):
		self.__DataLength=int(features.size/features.shape[0])
		self.__feature=np.zeros((39,self.__DataLength*150))
		#self.__Output=np.zeros(features.shape[1]*1950) # 13 * 150
		#return DataLength , feature, Output
		
	def ClassAndFeaturesSplit(self, features,types):
		#self.Length(features)
		
			
		self.__DataLength=int(features.size/features.shape[0])
		if types=="test":
			self.__prof=int((features.size/39))
		elif types =="train" :
			self.__prof=int((features.size/features.shape[1])/39)
		self.__feature=np.zeros((39,self.__DataLength*self.__prof))
		if (types=="train"):
			for i in range(0,self.__DataLength):
				idx=(i*self.__prof+np.arange(self.__prof))
			#idx_2=(i*1950+np.arange(1950))
				self.__feature[:,idx]=np.reshape(features[:,i],(39,self.__prof), order='F')
		elif (types=="test"):
			self.__feature=np.reshape(features,(39,self.__prof), order='F')
			#self.__Output[idx_2]=numpy.matlib.repmat(label,1,1950)
		# reshape all matrix in 3 vector -> MFCC, VMFCC, VVMFCC
		x_e=self.__feature[0,:].reshape(self.__feature[0,:].size, order='F')
		y_e=self.__feature[13,:].reshape(self.__feature[13,:].size, order='F')
		z_e=self.__feature[26,:].reshape(self.__feature[26,:].size, order='F')
		x=self.__feature[(1+np.arange(12)),:].reshape(self.__feature[(1+np.arange(12)),:].size, order='F')
		y=self.__feature[(14+np.arange(12)),:].reshape(self.__feature[(14+np.arange(12)),:].size, order='F')
		z=self.__feature[(27+np.arange(12)),:].reshape(self.__feature[(27+np.arange(12)),:].size, order='F')
	
		"""
		incr=0
		incr_e=0
		stdlx=0.0
		stdly=0.0
		stdlz=0.0
		stdlx_e=0.0
		stdly_e=0.0
		stdlz_e=0.0
		meanlx=0.0
		meanly=0.0
		meanlz=0.0
		meanlx_e=0.0
		meanly_e=0.0
		meanlz_e=0.0
		incrm=0
		incrm_e=0
		
		for i in range(x.size):
			if x[i]!=0.:
				meanlx+=x[i]
				meanly+=y[i]
				meanlz+=z[i]
				incrm+=1
			if i < x_e.size :
				if x_e[i]!=0.:
					meanlx_e+=x[i]
					meanly_e+=y[i]
					meanlz_e+=z[i]
					incrm_e+=1
		"""
		meanx=np.mean(x)#meanlx/incrm
		meany=np.mean(y)#meanly/incrm
		meanz=np.mean(z)#meanlz/incrm
		meanx_e=np.mean(x_e)#meanlx_e/incrm_e
		meany_e=np.mean(y_e)#meanly_e/incrm_e
		meanz_e=np.mean(z_e)#meanlz_e/incrm_e
		"""
		for i in range(x.size):
			if (x[i]!=0):# and y[i]!=0. and z[i]!=0.):
				stdlx+=(x[i]-meanx)**2
				stdly+=(y[i]-meany)**2
				stdlz+=(z[i]-meanz)**2
				if i < x_e.size :
					stdlx_e+=(x_e[i]-meanx_e)**2
					stdly_e+=(y_e[i]-meany_e)**2
					stdlz_e+=(z_e[i]-meanz_e)**2
					incr_e+=1
				incr+=1
		"""
		stdx=np.std(x)#math.sqrt(stdlx/incr)
		stdy=np.std(y)#math.sqrt(stdly/incr)
		stdz=np.std(z)#math.sqrt(stdlz/incr)
		stdx_e=np.std(x_e)#math.sqrt(stdlx_e/incr_e)
		stdy_e=np.std(y_e)#math.sqrt(stdly_e/incr_e)
		stdz_e=np.std(z_e)#math.sqrt(stdlz_e/incr_e)
		# 0 mean and one std
				## allocation of memory
		new_x=np.zeros(self.__DataLength*self.__prof*12)
		new_y=np.zeros(self.__DataLength*self.__prof*12)
		new_z=np.zeros(self.__DataLength*self.__prof*12)
		new_x_e=np.zeros(self.__DataLength*self.__prof)
		new_y_e=np.zeros(self.__DataLength*self.__prof)
		new_z_e=np.zeros(self.__DataLength*self.__prof)
				## operation
		for i in range(0,x.size):
			if x[i] != 0:
				new_x[i]=((x[i]-meanx)/stdx)-self.__center[0]
				new_y[i]=((y[i]-meany)/stdy)-self.__center[1]
				new_z[i]=((z[i]-meanz)/stdz)-self.__center[2]
				if i < x_e.size :
					new_x_e[i]=((x_e[i]-meanx_e)/stdx_e)-self.__center[0]
					new_y_e[i]=((y_e[i]-meany_e)/stdy_e)-self.__center[1]
					new_z_e[i]=((z_e[i]-meanz_e)/stdz_e)-self.__center[2]
			else :
				new_x[i]=0
				new_y[i]=0
				new_z[i]=0
				if i < x_e.size :
					new_x_e[i]=0
					new_y_e[i]=0
					new_z_e[i]=0
		# Paramter to create sphere with dataset
				## allocation of memory
		P_abs=np.zeros(self.__DataLength*self.__prof*12)
		P_abs_e=np.zeros(self.__DataLength*self.__prof)
		Q=np.zeros(P_abs.size)
		Q_e=np.zeros(P_abs_e.size)
				## operation
		P=(np.vstack((new_x,new_y,new_z))).T
		P_e=(np.vstack((new_x_e,new_y_e,new_z_e))).T
		for i in range(0, x.size):
			P_abs[i]=math.sqrt(new_x[i] **2 +new_y[i]**2 + new_z[i]**2)
			if i <x_e.size :
				P_abs_e[i]=math.sqrt(new_x_e[i] **2 +new_y_e[i]**2 + new_z_e[i]**2)
				if P_abs_e[i] !=0 :
					Q_e[i]=(self.__rayon/P_abs_e[i]).T
				else :
					Q_e[i]=0
			if P_abs[i] !=0 :
				Q[i]=(self.__rayon/P_abs[i]).T
			else :
				Q[i]=0
		
		# Sphere data
				## allocation of memory
		SphereData=np.zeros((self.__DataLength*self.__prof*12,3))
		SphereData_e=np.zeros((self.__DataLength*self.__prof*1,3))
		for i in range(0,3):
			SphereData[:,i]=Q*P[:,i]
			SphereData_e[:,i]=Q_e*P_e[:,i]
		"""" HERE HERE STOP """
		for i in range (0,3):
			for j in range(0,self.__DataLength*self.__prof*12):
				if math.isnan(SphereData[j,i])==True :
					SphereData[j,i]=0
			for k in range(0,self.__DataLength*self.__prof):
				if math.isnan(SphereData_e[k,i])==True :
					SphereData_e[k,i]=0
		feat_struct=np.concatenate((SphereData_e[:,0].reshape(1,self.__prof*self.__DataLength,order='F'),SphereData[:,0].reshape(12,self.__prof*self.__DataLength,order='F'),SphereData_e[:,1].reshape(1,self.__prof*self.__DataLength,order='F'),SphereData[:,1].reshape(12,self.__prof*self.__DataLength,order='F'),SphereData_e[:,2].reshape(1,self.__prof*self.__DataLength,order='F'),SphereData[:,2].reshape(12,self.__prof*self.__DataLength,order='F')),axis=0)

		features=np.zeros((39*self.__prof,self.__DataLength))
		for i in range (0,self.__DataLength):
			intermediaire=feat_struct[:,(i*self.__prof+np.arange(self.__prof))]
			features[:,i]=intermediaire.reshape(intermediaire.size, order='F')
		#print tools.bcolors.OKGREEN + "In Sphere - Calibration has been done ..." + tools.bcolors.ENDC
					
					
		return features

if __name__ == "__main__" :
	Sphere= Sphere_calibration()
	b=np.ones(5850)
	b[1]=2
	b[16]=100
	b[34]=4582
	b[5823]=18
	Sphere.ClassAndFeaturesSplit(b,1)
