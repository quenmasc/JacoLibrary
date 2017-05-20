# all import here
import os
import numpy as np
from pydub import AudioSegment
from scipy.io.wavfile import read
import inspect 
import mfccbuffer
import MFCC
import DSP
import struct
import fnmatch
import wave
import MachineLearning
from sklearn.externals import joblib
import tools
import Sphere

__author__="Quentin MASCRET <quentin.mascret.1 ulaval.ca>"
__date__="2017-05-03"
__version__="1.0-dev"



def ReadAudioFile(path):
    extension=os.path.splitext(path)[1]
    if extension=='.wav':
        f=open(path,'rb')
        data=f.read()
        data=np.fromstring(data, np.int16)
        x=np.array(data)
        return  x
    else :
        print "Error in ReadAudioFile() : NO FILE TYPE"

        return (-1,-1)

def FindWavFileAndStoreData():
    i=0

    os.chdir('speech/')
    listdirectory = os.listdir(".")
    for filename in listdirectory :
        if filename.endswith(".wav"):
            i+=1
	    data=ReadAudioFile(filename)
	    mfccs=WAV2MFCCs(data)
            classLabel=ClassAttribution(filename)
            struct=[classLabel,mfccs]
            FeaturesSaved(struct)
            print tools.bcolors.HEADER +"Features of", filename ," have been saved"  + tools.bcolors.ENDC
            print "remaining" ,len(listdirectory)-i
    print tools.bcolors.OKGREEN +"all done" +tools.bcolors.ENDC

def WAV2MFCCs(data,window_sample=200,window_shift=85):
     data=DSP.normalize(data,32768.0)
     buff=mfccbuffer.MFFCsRingBuffer()    
     mfcc=MFCC.MFCCs()
     nbFrame=(len(data)-window_sample)/window_shift
     for i in range(0,nbFrame):
	signal=np.array(data[(i*window_shift+np.arange(window_sample))])
	m=mfcc.MFCC2(signal)
	buff.extend2(m)
     mfccs, fl=buff.get()
     return mfccs

def ClassAttribution(endsfile):
    if fnmatch.fnmatch(endsfile,'*BACKWARD.wav' ):
        return 'Class_1'
    elif fnmatch.fnmatch(endsfile,'*FORWARD.wav' ):
        return 'Class_2'
    elif fnmatch.fnmatch(endsfile,'*LEFT.wav' ):
        return 'Class_3'
    elif fnmatch.fnmatch(endsfile,'*RIGHT.wav' ):
        return 'Class_4'
    elif fnmatch.fnmatch(endsfile,'*GOTO.wav' ):
        return 'Class_5'
    elif fnmatch.fnmatch(endsfile,'*READY.wav' ):
        return 'Class_6'
    elif fnmatch.fnmatch(endsfile,'*MODE.wav' ):
        return 'Class_7'
    else :
        return 'Class_8'

def FeaturesSaved(struct):
    os.chdir('../')
    if not os.path.exists(struct[0]) :
        os.makedirs(struct[0])
        print tools.bcolors.OKBLUE +"folder :" ,struct[0], "has been created" + tools.bcolors.ENDC
    os.chdir(struct[0])
    if not os.path.isfile(ClassDictionnaryFile(struct[0])):
        file(ClassDictionnaryFile(struct[0]),'a').close()
        np.savetxt(ClassDictionnaryFile(struct[0]),struct[1])
    else :
        data=np.loadtxt(ClassDictionnaryFile(struct[0]))
        data=np.vstack([data,struct[1]])
        np.savetxt(ClassDictionnaryFile(struct[0]),data)
    os.chdir('../speech')

def ClassDictionnaryFile(className):
    return {
        'Class_1' :'Class_1.txt',
        'Class_2' :'Class_2.txt',
        'Class_3' :'Class_3.txt',
        'Class_4' :'Class_4.txt',
        'Class_5' :'Class_5.txt',
        'Class_6' :'Class_6.txt',
        'Class_7' :'Class_7.txt',
        'Class_8' :'Class_8.txt',
        }[className]

def FolderClassDictionnary(listOfDirs):
     return { 
        'Class_1' : 1,
        'Class_2' : 2,
        'Class_3' : 3,
        'Class_4' : 4,
        'Class_5' : 5,
        'Class_6' : 6,
        'Class_7' : 7,
        'Class_8' : 8,
        }.get(listOfDirs,0) # zero is default class

def ClassName(Label):
     return { 
         1 : "BACKWARD",
         2 : "FORWARD",
         3 : "LEFT",
         4 : "RIGHT" ,
         5 : "GOTO",
         6 : "READY",
         7 : "MODE",
        }.get(Label,0)
    
def FistSVMClass(listOfDirs):
     return { 
        'Class_1' : 1,
        'Class_2' : 1,
        'Class_3' : 2,
        'Class_4' : 2,
        'Class_5' : 2,
        'Class_6' : 2,
        'Class_7' : 1,
        'Class_8' : 3,
        }.get(listOfDirs,0) # zero is default class

def ReadFeatureClass():
    listdirectory = os.listdir(".")
    Normalization=Sphere.Sphere_calibration()
    Features=np.array([]).reshape(5850,0)
    FeaturesLeft=np.array([]).reshape(5850,0)
    FeaturesRight=np.array([]).reshape(3120,0)
    ClassNormal=np.array([]).reshape(1,0)
    ClassLeft=np.array([]).reshape(1,0)
    ClassRight=np.array([]).reshape(1,0)
    ClassFistLevel=np.array([]).reshape(1,0)
    for filename in listdirectory :
        if FolderClassDictionnary(filename)>0:
            os.chdir(filename)
            data=Normalization.ClassAndFeaturesSplit((np.loadtxt(os.listdir(".")[0])).T)
            classFistLevel=np.matlib.repmat(FistSVMClass(filename),1,data.shape[1])
            classNormal=np.matlib.repmat(FolderClassDictionnary(filename),1,data.shape[1])
            os.chdir('../')
            Features=np.hstack([Features,data])
            if (FistSVMClass(filename)==1):
                classLeft=np.matlib.repmat(FolderClassDictionnary(filename),1,data.shape[1])
                ClassLeft=np.hstack([ClassLeft,classLeft])
                FeaturesLeft=np.hstack([FeaturesLeft,data])
            if (FistSVMClass(filename)==2):
                classRight=np.matlib.repmat(FolderClassDictionnary(filename),1,data.shape[1])
                ClassRight=np.hstack([ClassRight,classRight])
                FeaturesRight=np.hstack([FeaturesRight,data[(0+np.arange(3120))]])
            ClassFistLevel=np.hstack([ClassFistLevel,classFistLevel])
            ClassNormal=np.hstack([ClassNormal,classNormal])
    print tools.bcolors.OKGREEN + "In AudioIO - ReadFeatureClass : all features have been read." +tools.bcolors.ENDC
    return Features,FeaturesLeft, FeaturesRight , ClassLeft[0],ClassRight[0],ClassFistLevel[0],ClassNormal[0]


def SaveClassifier(modelName,svmClassifier):
    joblib.dump(svmClassifier,"SVModel/%s.pkl"%modelName)
    print tools.bcolors.OKGREEN + "In AudioIO - SaveClassifier : Model has been saved correctly" + tools.bcolors.ENDC
    
def LoadClassifier(SVMModelName):
    try : 
        model=joblib.load("/home/pi/libkindrv/PythonFile/SVModel/%s.pkl"%SVMModelName)
        print tools.bcolors.OKGREEN + "Classifier loaded %s"%SVMModelName + tools.bcolors.ENDC
        return model
    except IOError :
        print tools.bcolors.FAIL +"Unable to load the Classifier %s"%SVMModelName+tools.bcolors.ENDC
        return

    
def test():
    [features, featuresL, featuresR, classL, classR,ClassFistLevel, CN]=ReadFeatureClass()
    if len(features)==0 :
        print tools.bcolors.FAIL+ "In Classifier - Error : folders are empty"+tools.bcolors.ENDC
        return
    print tools.bcolors.HEADER +"Size of features :" , featuresL.shape , len(classL), featuresR.shape , len(classR),features.shape , len(ClassFistLevel) , "Features, FeaturesL , FeaturesR" + tools.bcolors.ENDC
    FistSvmModel=MachineLearning.TrainSVM_RBF_Features(features.T, CN)#ClassFistLevel
    SaveClassifier("SVM",FistSvmModel)
  #  print tools.bcolors.HEADER + "First SVM saved" + tools.bcolors.ENDC
 #   SecondSvmModel=MachineLearning.TrainSVM_RBF_Features(featuresL.T, classL)
  #  SaveClassifier("LeftSVM",SecondSvmModel)
 #   print tools.bcolors.HEADER + "Second SVM saved" + tools.bcolors.ENDC
 #   ThirdSvmModel=MachineLearning.TrainSVM_RBF_Features(featuresR.T, classR)
  #  SaveClassifier("RightSVM",ThirdSvmModel)
  #  print tools.bcolors.HEADER + "Third SVM saved" + tools.bcolors.ENDC
  #  print tools.bcolors.OKGREEN + "All classifiers have been saved" +tools.bcolors.ENDC
    
def train():
    [features, featuresL, featuresR, classL, classR,ClassFistLevel, CN]=ReadFeatureClass()
    if len(features)==0 :
        print tools.bcolors.FAIL + "In Classifier - Error : folders are empty"+tools.bcolors.ENDC
        return
    model=LoadClassifier("SVM")
  #  modelL=LoadClassifier("LeftSVM")
  #  modelR=LoadClassifier("RightSVM")
    SVM=MachineLearning.TrainBestParams(model.best_params_,features.T,CN)#ClassFistLevel
    print tools.bcolors.HEADER + "First SVM Trained" + tools.bcolors.ENDC
#    SVML=MachineLearning.TrainBestParams(modelL.best_params_,featuresL.T,classL)
 #   print tools.bcolors.HEADER + "Left SVM Trained" + tools.bcolors.ENDC
 #   SVMR=MachineLearning.TrainBestParams(modelR.best_params_,featuresR.T,classR)
 #   print tools.bcolors.HEADER + "Right SVM Trained" + tools.bcolors.ENDC
    print tools.bcolors.OKGREEN + "All SVM Trained correctly -> next step save them" + tools.bcolors.ENDC
    SaveClassifier("SVM_Trained",SVM)
    print tools.bcolors.HEADER + " SVM Trained saved" + tools.bcolors.ENDC
#    SaveClassifier("LeftSVM_Trained",SVML)
#    print tools.bcolors.HEADER + " Left SVM Trained saved" + tools.bcolors.ENDC
 #   SaveClassifier("RightSVM_Trained",SVMR)
 #   print tools.bcolors.HEADER + "Right SVM Trained saved" + tools.bcolors.ENDC
    print tools.bcolors.OKGREEN + "All SVM Trained have been saved" + tools.bcolors.ENDC
    
if __name__=='__main__' :
  # FindWavFileAndStoreData()
  test()
  train()
   #model=LoadClassifier("SVM_Trained")
   #modelL=0 #LoadClassifier("LeftSVM_Trained")
  #modelR=0 #LoadClassifier("RightSVM_Trained")
 # print(model)
 #  features=np.loadtxt('coeff.out')
 # print len(features)
#   R1 , R2 , P1 , P2=MachineLearning.ClassifierWrapper(model, modelL, modelR,features)
 #  print R1, R2

   
