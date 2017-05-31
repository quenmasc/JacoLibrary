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
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import StratifiedKFold
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import StandardScaler
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
    if R1 == 1 :
		R2=classifierL.predict(Vector)
		P2=classifierL.predict_proba(Vector)
    elif R1 == 2 :
        R2=classifierR.predict(Vector[0][(0+np.arange(3120))]).reshape(1,-1)
        P2=classifierR.predict_proba(Vector[0][(0+np.arange(3120))]).reshape(1,-1)
    return R1 , R2 , P1 , P2

def TrainBestParams(params,features,classLabel):
    svm=OneVsRestClassifier(SVC(probability=True, **params))
    svm.fit(features,classLabel)
    return svm

def NormalizeFeatures(features):
        # features matrix need to be a matrix with n rows coefficient per k colunm data
     print "normalization"


def C_Gamma(index):
	return { 
		1 : dict(estimator__gamma=np.logspace(-6,-2,40), estimator__C=np.logspace(-1,3,40)),
		2 : dict(estimator__gamma=np.logspace(-12,-4,40), estimator__C=np.logspace(-6,0,40)),
		3 : dict(estimator__gamma=np.logspace(-12,-3,40), estimator__C=np.logspace(0,20)),
        }.get(index) # zero is default class
        
def TrainSVM_RBF_Features(features,classLabel,index):

		scaler=StandardScaler()
		features=scaler.fit_transform(features)
    # paramgrid
		param_grid=C_Gamma(index)

    # cv
		cv = StratifiedShuffleSplit(classLabel,n_iter=20 , test_size=0.4, train_size=0.6,random_state=42)

    # grid
		print tools.bcolors.OKBLUE + "Running ..." + tools.bcolors.ENDC
		grid =GridSearchCV(OneVsRestClassifier(SVC(kernel="rbf")),param_grid=param_grid,cv=cv,verbose=20,n_jobs=2) # k=17 StratifiedKFold(classLabel,k=17)
		grid.fit(features,classLabel)
		return grid
    
def Splitfeatures(features, classLabel, pourcentOf):
    featuresTrain, featuresTest, ClassTrain, ClassTest = train_test_split(features,classLabel,test_size=pourcentOf,random_state=45)
    print tools.bcolors.OKGREEN + "In MachineLearning - Splitfeatures : featuresTrain and featuresTest have been generated with suceed" +tools.bcolors.ENDC
    return featuresTrain, featuresTest, ClassTrain ,ClassTest


