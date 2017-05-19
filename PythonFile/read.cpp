#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stdlib.h>
#include <stdio.h>
#include <sys/stat.h>
#include <cmath>
#include <unistd.h>
#include <string.h>
#include <thread>
//define FIFO_NAME "fifo"


int main (){
	system("gnome-terminal -x sh -c 'python SpeechRecognition.py &'");
	const char *fifo_name="fifo";
	int n;
	while(1){
	mknod(fifo_name,S_IFIFO | 0666,0);
	std::ifstream f(fifo_name);
	std::string(line);
	//getline(f,line);
	//printf("in");
	while(getline(f,line)){
	auto data_size=std::stoi(line);
	//std::cout << "Size" << data_size << std::endl;
	std::string data;
	
	if (!f.good()){
	//	std::cerr <<"read failed" << std::endl ;
	}
	{
		std::vector<char> buf(data_size);
		f.read(buf.data(),data_size);
		data.assign(buf.data(),buf.size());
	}
	n=std::stoi(data,nullptr,2);
	std::cout << "class is : " << n << std::endl;
}
}
}

