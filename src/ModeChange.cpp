#include "ModeChange.h"

namespace KinDrv{
	
	
	//parameters
int OldClass =0;
bool flag=true ;
	// methods

int ModeChange::classPCA(int classLabel){
	switch (classLabel){
			case 1 :
				return 1;
			case 2 :
				return 1;
			case 3 :
				return 1;
			case 4 :
				return 1;
			case 5 :
				return 2;
			case 6 :
				return 3;
			case 7 :
				return 4;
			default :
			return 0;
		}
}


ModeChange::ModeChange(void){
	}
ModeChange::~ModeChange(void){
	}
}
