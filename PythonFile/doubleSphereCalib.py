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
__date__="2017-07-19"
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

class Calculation:
		def __init__(self,path):
			self.__svm=AudioIO.LoadClassifier("SVM_Trained")
			self.__svmL=AudioIO.LoadClassifier("LeftSVM_Trained")
			self.__svmR=AudioIO.LoadClassifier("RightSVM_Trained")
			self.__F,self.__C=ImportData(path)
			self.__Sph_Cal=Sphere2.Sphere_calibration()
			self.__best_score_init=np.zeros((12),'f')
			self.__score_high=0.0
			self.__value=np.zeros((10),'f')
			
		def Score(self,best_score,x):
				local_score=0.0
				beta_score=0.0
				for l in range(12):
						local_score+=best_score[l]
						beta_score+=1-best_score[l]
				local_score=local_score/12
				beta_score=beta_score/12
				if local_score > self.__score_high :
					self.__best_score_init=best_score
					self.__score_high=local_score
					self.__value=x
					np.savetxt('Value_T_2_sphere_calib1.out',self.__value)
				return local_score, beta_score
						
				
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
				error_score=np.zeros((12),'i')
				error=1.0
				tri=np.zeros((12),'f')
				for i in range(column):
						classL=int( MachineLearning.ClassifierWrapper(self.__svm, self.__svmL, self.__svmR,features[:,i].reshape(1,-1))[1][0])
						Label=AudioIO.InvertClass(classL)
						if Label == Class[i]:
								best_score[self.InvertClass(Class[i])]+=1
						else :
							error_score[self.InvertClass(Label)]+=1
						test_score[self.InvertClass(Class[i])]+=1
				if np.sum(test_score)!=len(Class):
						print "Error"
				for i in range(12):
						best_score[i]=best_score[i]/test_score[i]
						if error_score[i]!=0:
							error+=error_score[i]
				#error_score.sort()
				tri=np.argsort(best_score)
				return best_score, error_score,tri
	
	
		def func1(self,x):
			featuresSphere=np.array([]).reshape(4680,0)
			RotationMatrix=Angle2RotationMatrix(x[6],x[7])
			RotationMatrix_e=Angle2RotationMatrix(x[8],x[9])
			center=np.zeros((6),'f')
			for i in range (len(center)) :
				center[i]=x[i]
			for l in range (self.__F.shape[1]):
				featuresSphere=np.hstack([featuresSphere,self.__Sph_Cal.DoubleSphere(self.__F[:,l],"test",center,RotationMatrix,RotationMatrix_e).reshape(4680,1)])
			curr_score, curr_error, tri =self.CompileSVMChecking(featuresSphere, self.__C)	
			#print curr_score
			score, error= self.Score(curr_score,x)
			print "score",score, "best", self.__score_high , "high ", self.__best_score_init,"\n focus ", error
			#print " *********************************\n"
			return  1-score #curr_error*error
			


class World(object):
    '''
        lower_bound and upper_bound refer to the min and max of the function to optimize respectively.
        number_of_genes correspond to the number of dimensions of the function to optimize.
        population_size Number of creature in a population
        number_of_generation correspond to the number of the main loop the algorithm will do
    '''
    def __init__(self, lower_bound, upper_bound, swarm_size_main_population, swarm_size_auxiliary_population,
                 fitness_function, swarm_confidence=2.0):
        self._random = np.random.RandomState()
        self._number_of_dimensions = number_of_dimensions
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._number_of_generation_swarm = number_of_generation_swarm
        self._swarm_size_main_population = swarm_size_main_population
        self._swarm_size_auxiliary_population = swarm_size_auxiliary_population

        #Swarm hyper-parameters
        self._swarm_confidence = swarm_confidence

        self._fitness_function = fitness_function

        # Create the main swarm responsible to explore the function
        self._swarm = Swarm(number_of_creatures_main_population=self._swarm_size_main_population,
                            number_of_creatures_auxiliary_population=self._swarm_size_auxiliary_population,
                            lower_bound=self._lower_bound, upper_bound=self._upper_bound, random=self._random)

        self._list_real_evaluation_position = []
        self._list_real_evaluation_fitness = []

    def run_world(self, max_evals):
        nmbr_evals, best_creature_fitness, best_creature_position = self._swarm.run_swarm(
            max_iter=self._number_of_generation_swarm, fitness_function=self._fitness_function, max_evals=max_evals)
        print "FINISHED"
        print "BEST POSITION FOUND"
        print best_creature_fitness
        print best_creature_position
        np.savetxt("data_2_sphere_calib1.out",best_creature_position)
        return nmbr_evals, best_creature_fitness, best_creature_position

dimensions = [10]
all_the_positions_with_curiosity = []
nmbr_repetition = 1
all_the_fitness_with_curiosity = np.zeros(nmbr_repetition)
swarm_size_main_population = 144
swarm_size_auxiliary_population = 48
number_of_evals = 1000
patient="Jean-Michel"
translation=Calculation("%s/"%patient)

for repeat in range(nmbr_repetition):
    print "Schwefel"
    i = 0
    for number_of_dimensions in dimensions:
        #print "Schwefel"
        lower_bound =np.array( [-10., -10., -10., -10., -10.,-10., -180., -90., -180.,-90.])
        upper_bound =np.array( [10., 10., 10., 10., 10., 10., 180., 90., 180., 90.])
        number_of_generation_swarm = 10000
        swarmProcess = World(lower_bound=lower_bound, upper_bound=upper_bound,
                             swarm_size_main_population=swarm_size_main_population,
                             swarm_size_auxiliary_population=swarm_size_auxiliary_population,
                             fitness_function=translation.func1)
        nmbr_evals, best_creature_fitness, best_creature_position = swarmProcess.run_world(number_of_evals)
        print "FINAL FITNESS FOUND: ", best_creature_fitness
        all_the_fitness_with_curiosity[repeat] = best_creature_fitness
        if repeat == 0:
            all_the_positions_with_curiosity.append(best_creature_position)
        print "TOTAL NUMBER EVALUATION: ", nmbr_evals
        i += 1
print patient
print "Average value found:"
print "AVERAGE: ", np.mean(all_the_fitness_with_curiosity), \
    " STD: ", np.std(all_the_fitness_with_curiosity)
print all_the_fitness_with_curiosity
f = open('result_100D', 'a')
f.write("Schwefel (100D):\n")
f.write("TAD-PSO:\n")
f.write(str(all_the_fitness_with_curiosity)+'\n')
f.write('AVERAGE: '+str(np.mean(all_the_fitness_with_curiosity))+'\n STD: '+str(np.std(all_the_fitness_with_curiosity)))
f.write('\n\n\n')
f.close()

			
"""		
class Particle:
    def __init__(self,x0):
        self.position_i=[]          # particle position
        self.velocity_i=[]          # particle velocity
        self.pos_best_i=[]          # best position individual
        self.err_best_i=-1          # best error individual
        self.err_i=-1               # error individual

        for i in range(0,num_dimensions):
            self.velocity_i.append(random.uniform(-1,1))
            self.position_i.append(x0[i])

    # evaluate current fitness
    def evaluate(self,costFunc):
        self.err_i=costFunc(self.position_i)

        # check to see if the current position is an individual best
        if self.err_i > self.err_best_i or self.err_best_i==-1: #<
            self.pos_best_i=self.position_i
            self.err_best_i=self.err_i

    # update new particle velocity
    def update_velocity(self,pos_best_g):
        w=0.5       # constant inertia weight (how much to weigh the previous velocity)
        c1=1        # cognative constant
        c2=2        # social constant

        for i in range(0,num_dimensions):
            r1=random.random()
            r2=random.random()

            vel_cognitive=c1*r1*(self.pos_best_i[i]-self.position_i[i])
            vel_social=c2*r2*(pos_best_g[i]-self.position_i[i])
            self.velocity_i[i]=w*self.velocity_i[i]+vel_cognitive+vel_social

    # update the particle position based off new velocity updates
    def update_position(self,bounds):
        for i in range(0,num_dimensions):
            self.position_i[i]=self.position_i[i]+self.velocity_i[i]

            # adjust maximum position if necessary
            if self.position_i[i]>bounds[i][1]:#>
                self.position_i[i]=bounds[i][1]

            # adjust minimum position if neseccary
            if self.position_i[i] < bounds[i][0]:#<
                self.position_i[i]=bounds[i][0]
                
class PSO():
    def __init__(self,costFunc,x0,bounds,num_particles,maxiter):
        global num_dimensions

        num_dimensions=len(x0)
        err_best_g=-1                   # best error for group
        pos_best_g=[]                   # best position for group

        # establish the swarm
        swarm=[]
        for i in range(0,num_particles):
            swarm.append(Particle(x0))

        # begin optimization loop
        i=0
        while i < maxiter:
            #print i,err_best_g
            # cycle through particles in swarm and evaluate fitness
            for j in range(0,num_particles):
                swarm[j].evaluate(costFunc)

                # determine if current particle is the best (globally)
                if swarm[j].err_i > err_best_g or err_best_g == -1: #<  / 1-
                    pos_best_g=list(swarm[j].position_i)
                    err_best_g=float(swarm[j].err_i)

            # cycle through swarm and update velocities and position
            for j in range(0,num_particles):
                swarm[j].update_velocity(pos_best_g)
                swarm[j].update_position(bounds)
            i+=1

        # print final results
        print 'FINAL:'
        print pos_best_g
        print err_best_g

if __name__ == "__PSO__":
		main()

#--- RUN ----------------------------------------------------------------------+
translation=Calculation("Roxane/")
initial=[2.5,2.5,2.5,2.5,2.5,2.5,25.0,25.0,25.0,25.0]               # initial starting location [x1,x2...]
bounds=[(-5.0,5.0),(-5.0,5.0),(-5.0,5.0),(-5.0,5.0),(-5.0,5.0),(-5.0,5.0),(-180.0,180.0),(-90.0,90.0),(-180.0,180.0),(-90.0,90.0)]  # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]
PSO(translation.func1,initial,bounds,num_particles=40,maxiter=100)
"""
