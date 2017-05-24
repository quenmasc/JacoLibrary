# all import here
import numpy as np
import math
import struct
import array
import time
import DSP
import wave
import os
import sys
import sklearn.svm
import sklearn.decomposition
import sklearn.ensemble
from sklearn.svm import SVC
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import StratifiedShuffleSplit
from sklearn.cross_validation import StratifiedKFold
import tools

__author__="Quentin MASCRET <quentin.mascret.1@ulaval.ca>"
__date__="2017-04-30"
__version__="1.0-dev"


def ClassifierWrapper(classifier,classifierL,classifierR, Vector):
    R1=-1
    P1=-1
    R2=-1
    P2=-1
    R1=classifier.predict(Vector)
    P1=classifier.predict_proba(Vector)
 #   if R1 == 1 :
     #   R2=classifierL.predict(Vector)
      #  P2=classifierL.predict_proba(Vector)
   # elif R1 == 2 :
      #  R2=classifierR.predict(Vector[(0+np.arange(3120))])
       # P2=classifierR.predict_proba(Vector[(0+np.arange(3120))])
    return R1 , R2 , P1 , P2

def TrainBestParams(params,features,classLabel):
    svm=sklearn.svm.SVC(probability=True,**params)
    svm.fit(features,classLabel)
    return svm

def NormalizeFeatures(features):
        # features matrix need to be a matrix with n rows coefficient per k colunm data
     print "normalization"

def TrainSVM_RBF_Features(features,classLabel):

    # splt features into class test and train
   # featuresTrain,featuresTest ,classTrain, ClassTest = MachineLearning.Splitfeatures(features.T,classL.T,0.9)

    # C and Gamma range
    C= np.logspace(-6,3,20) #20
    Gamma=np.logspace(-9,3,20)#20

    # paramgrid
    param_grid=dict(gamma=Gamma, C=C)

    # cv
   # cv = StratifiedShuffleSplit(n_splits=50 , test_size=0.1, random_state=42)

    # grid
    print tools.bcolors.OKBLUE + "Running ..." + tools.bcolors.ENDC
    grid =GridSearchCV(SVC(),param_grid=param_grid,cv=StratifiedKFold(classLabel,k=17),verbose=40,n_jobs=2) # k=17
    grid.fit(features,classLabel)
    return grid
    
def Splitfeatures(features, classLabel, pourcentOf):
    featuresTrain, featuresTest, ClassTrain, ClassTest = train_test_split(features,classLabel,test_size=pourcentOf,random_state=45)
    print tools.bcolors.OKGREEN + "In MachineLearning - Splitfeatures : featuresTrain and featuresTest have been generated with suceed" +tools.bcolors.ENDC
    return featuresTrain, featuresTest, ClassTrain ,ClassTest


