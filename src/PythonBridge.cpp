#include "PythonBridge.h"
namespace KinDrv{
/* The code below is from Ulysse Project */
PyObject *pNameSVM , *pModuleSVM , *pDictSVM , *pClassSVM , *pInstanceSVM;
PyThreadState *mainThreadState , *myThreadState , *tempState ;
PyInterpreterState *mainInterpreterState;

PythonBridge::PythonBridge(){
	const char *python_information[]={"PythonFile","SpeechRecognition","Speech_Recognition"};
	// build project name
	PyEval_InitThreads();
	Py_Initialize();
	
	//mainThreadState = PyThreadState_Get();
	//mainInterpreterState = mainThreadState -> interp;
	//myThreadState = PyThreadState_New(mainInterpreterState);
	//PyEval_ReleaseLock();
	//PyEval_AcquireLock();
	//tempState= PyThreadState_Swap(myThreadState);
	
	//PyThreadState *state = PyThreadState_Get();
	//PyInterpreterState* interpreterState = state -> interp;

	PyRun_SimpleString("import sys ; sys.path.insert(0,'/home/pi/libkindrv/PythonFile')");
	pNameSVM=PyString_FromString(python_information[1]);
	// load the module project
	pModuleSVM=PyImport_Import(pNameSVM);
	// pdict  is q borrewd reference
	pDictSVM=PyModule_GetDict(pModuleSVM);
	// Build the name of the callable class 
	pClassSVM=PyDict_GetItemString(pDictSVM,python_information[2]);
	
	pInstanceSVM=NULL;
	// create an instance of the class
	if(PyCallable_Check(pClassSVM)){
		pInstanceSVM=PyObject_CallObject(pClassSVM,NULL);
	}
	else {
		PyErr_Print();
	}
	//Py_DECREF(pModuleSVM);
	//Py_DECREF(pNameSVM);
	//PyThreadState_Swap(tempState);
	//PyThreadState_Delete(myThreadState);
	//Py_Finalize();
}
PythonBridge::~PythonBridge(){};
void PythonBridge::finalize_python(){
	Py_DECREF(pInstanceSVM);
	Py_DECREF(pDictSVM);
	Py_DECREF(pModuleSVM);
	Py_DECREF(pNameSVM);
	Py_Finalize();
}

void PythonBridge::Running_python(){
	PyObject_CallMethod(pInstanceSVM,(char*)"Recorder",(char*)"");
}

int PythonBridge::ClassValue(){
	int Classification=0;
	PyObject *pValue ;
	pValue=PyObject_CallMethod(pInstanceSVM,(char*)"read_Pipe",(char*)"O");
	if (pValue!=NULL){
		Classification=PyInt_AsLong(pValue);
		printf("value : %ld",PyInt_AsLong(pValue));
		Py_DECREF(pValue);
	}
	return Classification;
}

void PythonBridge::ClassValue2(){
	PyObject_CallMethod(pInstanceSVM,(char*)"SVM",(char*)"");
}

}




