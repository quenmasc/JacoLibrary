import numpy as np
import numpy.matlib
import tools
import math
import struct
import array
import time
import tools
import cPickle
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from multiprocessing import Pool
 

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-05-20"
__version__="1.0-dev"

class Sphere_calibration(object):
	def __init__(self):
		self.__rayon=1.0
		self.__center=np.array([0,0,0])
	
		
	def ClassAndFeaturesSplit(self, features,types):
		
			
		self.__DataLength=int(features.size/features.shape[0])
		if types=="test" :
			self.__prof=int((features.size/39))
		elif types=="train" :
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
		x=self.__feature[(0+np.arange(13)),:].reshape(self.__feature[(0+np.arange(13)),:].size, order='F')
		y=self.__feature[(13+np.arange(13)),:].reshape(self.__feature[(13+np.arange(13)),:].size, order='F')
		z=self.__feature[(26+np.arange(13)),:].reshape(self.__feature[(26+np.arange(13)),:].size, order='F')
		if (types == "train"):
		
		# mean and std of x, y and z
			meanx=np.mean(x)
			meany=np.mean(y)
			meanz=np.mean(z) 
			stdx=np.std(x)
			stdy=np.std(y)
			stdz=np.std(z)
			fo=open("/home/pi/libkindrv/PythonFile/Properties_file/Mean_and_Std","wb")
			cPickle.dump(meanx,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			cPickle.dump(meany,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			cPickle.dump(meanz,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			cPickle.dump(stdx,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			cPickle.dump(stdy,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			cPickle.dump(stdz,fo,protocol=cPickle.HIGHEST_PROTOCOL)
			fo.close()
			
		elif (types == "test" ):
			"""
			try :
				fl=open("/home/pi/libkindrv/PythonFile/Properties_file/Mean_and_Std","rb")
			except IOError :
				print tools.bcolors.FAIL + "In Sphere - unable to open Mean and Std file" + tools.bcolors.ENDC
				return
			try :
				meanx=cPickle.load(fl)
				meany=cPickle.load(fl)
				meanz=cPickle.load(fl)
				stdx=cPickle.load(fl)
				stdy=cPickle.load(fl)
				stdz=cPickle.load(fl)
			except :
				fl.close()
			fl.close()
			"""
			meanx=np.mean(x)
			meany=np.mean(y)
			meanz=np.mean(z)
			incr=0
			stdlx=0.0
			stdly=0.0
			stdlz=0.0
			for i in range(x.size):
                                if (x[i]!=0 and y[i]!=0 and z[i]!=0):
                                        stdlx+=(x[i]-meanx)**2
                                        stdly+=(y[i]-meany)**2
                                        stdlz+=(z[i]-meanz)**2
                                        incr+=1
			stdx=math.sqrt(stdlx/incr)
			stdy=math.sqrt(stdly/incr)
			stdz=math.sqrt(stdlz/incr)
			"""
			meanx=np.mean(x)
			meany=np.mean(y)
			meanz=np.mean(z) 
			stdx=np.std(x)
			stdy=np.std(y)
			stdz=np.std(z)
			"""
		# 0 mean and one std
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
		if types == "test":
				"""
				try :
						fl=open("/home/pi/libkindrv/PythonFile/Properties_file/PatientCalibration","rb")
				except IOError :
						print tools.bcolors.FAIL + "In Sphere - unable to open Patient Calibration" + tools.bcolors.ENDC
						return
				try :
						Theta=cPickle.load(fl)
						Phi=cPickle.load(fl)
				except :
						fl.close()
				fl.close()
				"""
				Rotation=self.Angle2RotationMatrix(-18.4143,-12.8245)
				SphereData=SphereData.dot(Rotation)
		feat_struct=np.concatenate((SphereData[:,0].reshape(13,self.__prof*self.__DataLength,order='F'),SphereData[:,1].reshape(13,self.__prof*self.__DataLength,order='F'),SphereData[:,2].reshape(13,self.__prof*self.__DataLength,order='F')),axis=0)

				## allocation of memory
		features=np.zeros((39*self.__prof,self.__DataLength))
		for i in range (0,self.__DataLength):
			intermediaire=feat_struct[:,(i*self.__prof+np.arange(self.__prof))]
			features[:,i]=intermediaire.reshape(intermediaire.size, order='F')
		print tools.bcolors.OKGREEN + "In Sphere - Calibration has been done ..." + tools.bcolors.ENDC
					
					
		return features
		
	def Angle2RotationMatrix(self,Theta,Phi):
			
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
				np.savetxt('matr.out',RotationPhi)
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
				np.savetxt('mat.out',RotationMatrix)
				return RotationMatrix
	
	def SphereAxis(self, features,Center):
		self.__DataLength=int(features.size/features.shape[0])
		self.__prof=int((features.size/39))
		
		self.__feature=np.zeros((39,self.__DataLength*self.__prof))
		self.__feature=np.reshape(features,(39,self.__prof), order='F')
		
		# reshape all matrix in 3 vector -> MFCC, VMFCC, VVMFCC
		x=self.__feature[(0+np.arange(13)),:].reshape(self.__feature[(0+np.arange(13)),:].size, order='F')
		y=self.__feature[(13+np.arange(13)),:].reshape(self.__feature[(13+np.arange(13)),:].size, order='F')
		z=self.__feature[(26+np.arange(13)),:].reshape(self.__feature[(26+np.arange(13)),:].size, order='F')
		"""
		meanx=np.mean(x)
		meany=np.mean(y)
		meanz=np.mean(z) 
		stdx=np.std(x)
		stdy=np.std(y)
		stdz=np.std(z)
		"""
		meanx=np.mean(x)
		meany=np.mean(y)
		meanz=np.mean(z)
		incr=0
		stdlx=0.0
		stdly=0.0
		stdlz=0.0
		for i in range(x.size):
			if (x[i]!=0 and y[i]!=0 and z[i]!=0):
					stdlx+=(x[i]-meanx)**2
					stdly+=(y[i]-meany)**2
					stdlz+=(z[i]-meanz)**2
					incr+=1
		stdx=math.sqrt(stdlx/incr)
		stdy=math.sqrt(stdly/incr)
		stdz=math.sqrt(stdlz/incr)	
		
		# 0 mean and one std
				## allocation of memory
		new_x=np.zeros(self.__DataLength*self.__prof*13)
		new_y=np.zeros(self.__DataLength*self.__prof*13)
		new_z=np.zeros(self.__DataLength*self.__prof*13)
		P_abs=np.zeros(self.__DataLength*self.__prof*13)
		Q=np.zeros(x.size)
				## operation
		for i in range(0,x.size):
			if x[i] != 0:
				new_x[i]=((x[i]-meanx)/stdx)-Center[0]
				new_y[i]=((y[i]-meany)/stdy)-Center[1]
				new_z[i]=((z[i]-meanz)/stdz)-Center[2]
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
		return SphereData
		
	def Sphere2Vector(self,features,Center,Theta,Phi):
		SphereData=self.SphereAxis(features, Center)
		Rotation=self.Angle2RotationMatrix(Theta,Phi)
		SphereData=SphereData.dot(Rotation)
		feat_struct=np.concatenate((SphereData[:,0].reshape(13,self.__prof*self.__DataLength,order='F'),SphereData[:,1].reshape(13,self.__prof*self.__DataLength,order='F'),SphereData[:,2].reshape(13,self.__prof*self.__DataLength,order='F')),axis=0)

				## allocation of memory
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
