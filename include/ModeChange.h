
#include <stdio.h>
#include <stdlib.h>


namespace KinDrv{
	class  ModeChange{
		public :
			bool flag;
			int OldClass;
			int classPCA(int classLabel);
			ModeChange();
			~ModeChange();
			
	};
	
}

