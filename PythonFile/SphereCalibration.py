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
import MachineLearning

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
				print tools.bcolors.OKBLUE + "Sphere Calibration" + tools.bcolors.ENDC
				tools.printProgressBar(0,3,prefix='Progress',suffix='Complete',decimals=1, length=50)
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
				tools.printProgressBar(1,3,prefix='Progress',suffix='Complete',decimals=1, length=50)
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
				tools.printProgressBar(2,3,prefix='Progress',suffix='Complete',decimals=1, length=50)
				# Sphere data
				## allocation of memory
				SphereData=np.zeros((self.__DataLength*self.__prof*13,3))
				for i in range(0,3):
						SphereData[:,i]=Q*P[:,i]
						for j in range(0,self.__DataLength*self.__prof*13):
								if math.isnan(SphereData[j,i])==True :
										SphereData[j,i]=0
			
				tools.printProgressBar(3,3,prefix='Progress',suffix='Complete',decimals=1, length=50)
				# KMEANS below
				mu=np.zeros((self.__nClusters,nClass*3),'f')
				Theta=np.zeros((nClass,self.__nClusters),'f')
				Phi=np.zeros((nClass,self.__nClusters),'f')
				print tools.bcolors.OKBLUE + "Kmeans calculation in progress" + tools.bcolors.ENDC
				tools.printProgressBar(0,nClass,prefix='Progress',suffix='Complete',decimals=1, length=50)
				for i in range(1,nClass+1):
					km=KMeans(n_clusters=self.__nClusters,init=self.__initCentroid,n_init=1).fit(SphereData[self.__Label.T==i,:])
					mu[:,(i-1)*3+np.arange(3)]=km.cluster_centers_
					Angle=self.SphericalAngle(km.cluster_centers_.T)
					Theta[i-1,:]=Angle[0,:]
					Phi[i-1,:]=Angle[1,:]
					tools.printProgressBar(i,nClass,prefix='Progress',suffix='Complete',decimals=1, length=50)
				#np.savetxt('a.out',mu.T)
				#np.savetxt('phi.out',Phi.T)
				#np.savetxt('theta.out',Theta.T)
				params=np.zeros((2),'i')
				params[0]=self.__DataLength
				params[1]=self.__prof
				return Theta.T , Phi.T , SphereData,  params
				
		def SphericalAngle(self,mu):
				n=mu.shape[1]
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
		
		def Angle2Coordinated(self,Theta,Phi):
				x=math.sin(math.radians(Phi))*math.cos(math.radians(Theta))
				y=math.sin(math.radians(Phi))*math.sin(math.radians(Theta))
				z=math.cos(math.radians(Phi))
				return x,y,z
		
				
		def ImportData(self,path):
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
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=50)
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
						tools.printProgressBar(i,len(listdirectory),prefix='Progress',suffix='Complete',decimals=1, length=50)
				os.chdir('../')
				# return 
				np.savetxt('b.out', ClassNormal)
				return Features, ClassNormal[0],12
		
		def CalculateDiffAngle(self,AngleData, Angle):
				ThetaData=AngleData[0]
				PhiData=AngleData[1]
				Theta=Angle[0]
				Phi=Angle[1]
				# get size of matrix -> size of Phi and Theta must be the same
				row, column=ThetaData.shape
				PhiDiff=np.zeros((row,column),'f')
				ThetaDiff=np.zeros((row,column),'f')
				for i in range(row):
						for j in range (column):
								PhiDiff[i,j]=PhiData[i,j]-Phi[i,j]
								ThetaDiff[i,j]=ThetaData[i,j]-Theta[i,j]
				"""
				if (np.std(PhiDiff,axis=0)<=1):
						PhiDiff=np.mean(PhiDiff,axis=0)
				if (np.std(ThetaDiff,axis=0)<=1):
						ThetaDiff=np.mean(ThetaDiff,axis=0)
				"""
				return ThetaDiff, PhiDiff
		def SphereData2FeaturesMAtrix(self,SphereData,params):
				feat_struct=np.concatenate((SphereData[:,0].reshape(13,params[1]*params[0],order='F'),SphereData[:,1].reshape(13,params[1]*params[0],order='F'),SphereData[:,2].reshape(13,params[1]*params[0],order='F')),axis=0)

				## allocation of memory
				features=np.zeros((39*params[1],params[0]))
				
				for i in range (0,params[0]):
						intermediaire=feat_struct[:,(i*params[1]+np.arange(params[1]))]
						features[:,i]=intermediaire.reshape(intermediaire.size, order='F')
				return features
				
		def Angle2RotationMatrix(self,Theta,Phi):
			
				#define new vector director
				u=np.zeros((3),'f')
				u[0]=math.sin(math.radians(Theta))
				u[1]=-math.cos(math.radians(Theta))
				
				# some angles
				cosPhi=math.cos(math.radians(Phi))
				sinPhi=math.sin(math.radians(Phi))
				
				# Phi Rotation
				RotationPhi=np.zeros((3,3),'f')
				RotationPhi[0,0]=u[0]**2+(1-u[0]**2)*cosPhi
				RotationPhi[0,1]=-u[0]*u[1]*(1-cosPhi)
				RotationPhi[0,2]=u[1]*cosPhi
				RotationPhi[1,0]=-u[0]*u[1]*(1-cosPhi)
				RotationPhi[1,1]=u[1]**2+(1-u[1]**2)*cosPhi
				RotationPhi[1,2]=-u[0]*sinPhi
				RotationPhi[2,0]=-u[1]*sinPhi
				RotationPhi[2,1]=u[0]*sinPhi
				RotationPhi[2,2]=0
				
				# Theta Rotation
				RotationTheta=np.zeros((3,3),'f')
				RotationTheta[0,0]=u[1]
				RotationTheta[0,1]=u[0]
				RotationTheta[0,2]=0
				RotationTheta[1,0]=-u[0]
				RotationTheta[1,1]=u[1]
				RotationTheta[1,2]=0
				RotationTheta[2,0]=0
				RotationTheta[2,1]=0
				RotationTheta[2,2]=1
				
				RotationMatrix=RotationTheta.dot(RotationPhi)
				return RotationMatrix
		
		def CompileSVMChecking(self,svm,svmL,svmR,features, Class):
				best_score=np.zeros((12),'f')
				test_score=np.zeros((12),'i')
				ligne,column=features.shape
				for i in range(column):
						classL=int(MachineLearning.ClassifierWrapper(svm, svmL, svmR,features[:,i].reshape(1,-1))[1][0])
						Label=AudioIO.InvertClass(classL)
						if Label == Class[i]:
								best_score[Class[i]-1]+=1
						test_score[Class[i]-1]+=1
				for i in range(12):
						best_score[i]=best_score[i]/test_score[i]
				return best_score
				
		def main(self):
				svm=AudioIO.LoadClassifier("SVM_Trained")
				svmL=AudioIO.LoadClassifier("LeftSVM_Trained")
				svmR=AudioIO.LoadClassifier("RightSVM_Trained")
				DataSetPath="DataBase/"
				print tools.bcolors.OKGREEN + "DataBase Treatment" + tools.bcolors.ENDC
				F,C,n=self.ImportData(DataSetPath)
				ThetaData, PhiData, SphereData, params =self.Sphere(F,C,n)
				print tools.bcolors.OKGREEN + "Treatment complete" + tools.bcolors.ENDC
				
				
				## put here newdata
				AngleData=[ThetaData,PhiData]
				Angle=[ThetaData,PhiData]
				T,P=self.CalculateDiffAngle(AngleData, Angle)
				k=0
				tools.printProgressBar(k,6*12,prefix='Progress',suffix='Complete',decimals=1, length=50)
				# check last angle point (define  z rotation throughout matrix)
				for i in range (1,7):
						for j in range (12):#self.__nClusters):
								RotationMatrix=self.Angle2RotationMatrix(T[i,j],P[i,j])
								Data=SphereData.dot(RotationMatrix) #spheredata2 instead of SphereData -> new Data 
								features=self.SphereData2FeaturesMAtrix(Data,params)
								best_score=self.CompileSVMChecking(svm,svmL,svmR,features, C)
								k+=1
								tools.printProgressBar(k,6*12,prefix='Progress',suffix='Complete',decimals=1, length=50)
				print best_score
if __name__=='__main__' :
		 Calibration=Sphere_Calibrator(7,"Quentin")
		 Calibration.main()

