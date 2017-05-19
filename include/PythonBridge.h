#include <python2.7/Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <string>
namespace KinDrv {
class PythonBridge {
	public :
		PythonBridge();
		~PythonBridge();
		void finalize_python();
		void Running_python();
		int ClassValue();
		void ClassValue2();
};
}
