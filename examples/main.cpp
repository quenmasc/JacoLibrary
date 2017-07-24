#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <thread>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sys/stat.h>
#include <libkindrv/kindrv.h>
#include <queue>
#include <string>
#include <cstdlib>
#include <iomanip>

#define RED "\x1b[31m"
#define GREEN "\x1b[32m"
#define BLUE "\x1b[34m"
#define RESET "\x1b[0m"

using namespace KinDrv;
PythonBridge Bridge ;
int flag_Mode =false ;
bool flag_Goto = false ;
int last_Mode_Call =16;
int before_Mode_3_call=0 ;
int OpenClose=0;
/* JACO ARM INITIALIZATION */

int
goto_retract(JacoArm *arm)
{
  // this can only be achieved from HOME position. Otherwise the arm
  // will move to HOME. You'll probably need to uncomment the gripper movements
  // in order for this to work. Or even better, implement moving to HOME position,
  // which could be triggered before going to RETRACT ;)
  jaco_retract_mode_t mode = arm->get_status();
  switch( mode ) {
    case MODE_READY_TO_RETRACT:
      // is currently on the way to RETRACT. Need 2 button presses,
      // 1st moves towards HOME, 2nd brings it back to its way to RETRACT
      arm->push_joystick_button(2);
      arm->release_joystick();
      arm->push_joystick_button(2);
      break;

    case MODE_READY_STANDBY:
    case MODE_RETRACT_TO_READY:
      // just 1 button press needed
      arm->push_joystick_button(2);
      break;
    case MODE_NORMAL_TO_READY:
    case MODE_NORMAL:
    case MODE_NOINIT:
      printf("cannot go from NORMAL/NOINIT to RETRACT \n");
      return 0;
      break;

    case MODE_ERROR:
      printf("some error?! \n");
      return 0;
      break;

    case MODE_RETRACT_STANDBY:
      printf("nothing to do here \n");
      return 1;
      break;
  }

  while( mode != MODE_RETRACT_STANDBY ) {
    usleep(1000*10); // 10 ms
    mode = arm->get_status();
  }
  arm->release_joystick();


  return 1;
}



int
goto_home(JacoArm *arm)
{
  // going to HOME position is possible from all positions. Only problem is,
  // if there is some kinfo of error
  jaco_retract_mode_t mode = arm->get_status();
  switch( mode ) {
    case MODE_RETRACT_TO_READY:
      // is currently on the way to HOME. Need 2 button presses,
      // 1st moves towards RETRACT, 2nd brings it back to its way to HOME
      arm->push_joystick_button(2);
      arm->release_joystick();
      arm->push_joystick_button(2);
      break;


    case MODE_NORMAL_TO_READY:
    case MODE_READY_TO_RETRACT:
    case MODE_RETRACT_STANDBY:
    case MODE_NORMAL:
    case MODE_NOINIT:
      // just 1 button press needed
      arm->push_joystick_button(2);
      break;

    case MODE_ERROR:
      return 0;
      break;

    case MODE_READY_STANDBY:
      return 1;
      break;
  }

  while( mode != MODE_READY_STANDBY ) {
    usleep(1000*10); // 10 ms
    mode = arm->get_status();
    if( mode == MODE_READY_TO_RETRACT ) {
      arm->release_joystick();
      arm->push_joystick_button(2);
    }
  }
  arm->release_joystick();

  return 1;
}

void ModeCHange(JacoArm *arm,jaco_joystick_axis_t axes, int OldClass, int n){
	switch (n){
			case 6 :
				if(OldClass!=6){
					jaco_retract_mode_t mode = arm->get_status();
					arm->release_joystick();
					while(mode !=MODE_READY_STANDBY){
							//arm->release_joystick();
							arm->push_joystick_button(2);
							mode = arm->get_status();
				
							//usleep(5e6);
							//arm->release_joystick();
					}
					arm->release_joystick();
				}
				break;
			case 16 :
						switch (last_Mode_Call){
								case 16 :
										last_Mode_Call=16;
										flag_Mode=false;
										break ;
								case 17 : 
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(0);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=16;
										flag_Mode=false;
										//printf("Mode one selected\n");
										break ;
								default :
										if (before_Mode_3_call==16){
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												last_Mode_Call=16;
												flag_Mode=false;
												//printf("Mode one selected\n");
												break ;
											}
											else {
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												last_Mode_Call=16;
												flag_Mode=false;
												//printf("Mode one selected\n");
												break ;
											}
							}
				
				break;
			case 17 :
							switch (last_Mode_Call){
								case 17 :
										last_Mode_Call=17;
										flag_Mode=false;
										break ;
								case 16 : 
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(0);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=17;
										flag_Mode=false;
										//printf("Mode two selected\n");
										break ;
								default : 
										if (before_Mode_3_call==17){
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												last_Mode_Call=17;
												flag_Mode=false;
												//printf("Mode two selected\n");
												break ;
											}
											else {
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												arm->push_joystick_button(0);
												usleep(50000);
												arm->release_joystick();
												usleep(50000);
												last_Mode_Call=17;
												flag_Mode=false;
												//printf("Mode two selected\n");
												break ;
											}
							}
				break ;
			case 14 :
						switch (last_Mode_Call){
								case 14 :
										last_Mode_Call=14;
										switch (OpenClose){
												case 0 : 
													flag_Mode=false;
													OpenClose=1;
													break ;
												case 1 :
													axes.trans_lr +=0.5;
													arm->move_joystick_axis(axes);
													usleep(1000);
													arm->release_joystick();
													flag_Mode=false;
													break ;
												}
										break ;
						
		case 15 :
										last_Mode_Call=14;
										OpenClose=1;
										flag_Mode=false;
										break ;
								case 16 :
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(1);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=14;
										flag_Mode=false;
										before_Mode_3_call=16;
										//printf("Mode three selected\n");
										break ;
										
								case 17 :
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(1);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=14;
										flag_Mode=false;
										before_Mode_3_call=17;
										//printf("Mode three selected\n");
										break ;
										
							}
				break ;
				
				case 15 :
						switch (last_Mode_Call){
								case 14 :
										last_Mode_Call=15;
										flag_Mode=false;
										OpenClose=0;
										break ;
								case 15 :
										last_Mode_Call=15;
										switch (OpenClose){
												case 1 : 
													flag_Mode=false;
													OpenClose=0;
													break ;
												case 0 :
													axes.trans_lr -=0.5;
													arm->move_joystick_axis(axes);
													usleep(1000);
													arm->release_joystick();
													flag_Mode=false;
													break ;
												}
										break ;
								case 16 :
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(1);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=15;
										flag_Mode=false;
										before_Mode_3_call=16;
										//printf("Mode three selected 16 \n");
										break ;
										
								case 17 :
										arm->release_joystick();
										usleep(50000);
										arm->push_joystick_button(1);
										usleep(50000);
										arm->release_joystick();
										usleep(50000);
										last_Mode_Call=15;
										flag_Mode=false;
										before_Mode_3_call=17;
										//printf("Mode three selected 17\n");
										break ;
										
							}
				
				break ;
			case 1 :
				//if(OldClass!=1){
					axes.trans_fb +=0.5;
					arm->move_joystick_axis(axes);
					usleep(1000);
					arm->release_joystick();
			//}
			break;
			case 2 :
			//	if(OldClass!=2){
					axes.trans_fb -=0.5;
					arm->move_joystick_axis(axes);
					usleep(1000);
					arm->release_joystick();
			//}
			break;
			case 3 :
			//	if(OldClass!=3){
					axes.trans_lr +=0.5;
					arm->move_joystick_axis(axes);
					
					usleep(1000);
					arm->release_joystick();
			//	}
			break;
			case 4 :
			//	if(OldClass!=4){
					axes.trans_lr -=0.5;
					arm->move_joystick_axis(axes);
					usleep(1000);
					arm->release_joystick();
			//	}
			break;
			case 12 :
					axes.trans_rot +=0.5;
					arm->move_joystick_axis(axes);
					usleep(1000);
					arm->release_joystick();
			break ;
			case 18 :
					usleep(1000);
					arm->release_joystick();
			break ;
			case 13 :
					axes.trans_rot -=0.5;
					arm->move_joystick_axis(axes);
					usleep(1000);
					arm->release_joystick();
			break ;
			default :
				OldClass=0;
				break;
	}
}


 /*My THREAD */

void PythonRoutine(){
	//PyGILState_STATE gstate=PyGILState_Ensure();
	Bridge.Running_python();
	//PyGILState_Release(gstate);
	//while(1){}
}



void PipeClass(JacoArm *arm,jaco_joystick_axis_t axes, std::queue<int> &my_queue ){
	sleep(2);
	std::string mode;
	std::string keyboard;
	std::string word ;
	std::string status;
	mode="TRANSLATION";
	word="READY";
	status="WAITING ORDER";
	
	const char *fifo_name="/home/pi/libkindrv/examples/build/fifo";
	std::cout << "Pipe is opened" << std::endl;
	int n;
	while(1){
	mknod(fifo_name,S_IFIFO | 0666,0);
	std::ifstream f(fifo_name);
	std::string(line);
	while(getline(f,line)){
	auto data_size=std::stoi(line);
	std::string data;
	if (!f.good()){
	}
	{
		std::vector<char> buf(data_size);
		f.read(buf.data(),data_size);
		data.assign(buf.data(),buf.size());
	}
	n=std::stoi(data,nullptr,2);
	my_queue.push(n);
	
	switch (n){
		case 1 : 
			word="BACKWARD";
			status="RUNNING";
			break;
		case 2 :
			word="FORWARD";
			status="RUNNING";
			break;
		case 3 :
			word="LEFT";
			status="RUNNING";
			break;
		case 4 :
			word= "RIGHT";
			status="RUNNING";
			break;
		case 6 :
			word= "READY";
			status="WAITING ORDER";
			break;
		case 12 :
			word= "UP";
			status="RUNNING";
			break;
		case 13 :
			word= "DOWN";
			status="RUNNING";
			break;
		case 14 :
			word= "OPEN";
			mode="GRIPPER";
			break;
		case 15 :
			word= "CLOSE";
			mode="GRIPPER";
			status="RUNNING";
			break;
		case 18 :
			word= "STOP";
			status="WAITING ORDER";
			break;
		case 16 :
			mode="TRANSLATION";
			status="WAITING ORDER";
			break;
		case 17 :
			mode= "ROTATION";
			status="WAITING ORDER";
			break;
		default :
			break;
	}
	std::system("clear");
	printf(GREEN"****************************************************************************" RESET "\n");
	printf(GREEN"*  ____    ___  ____  _____    _____  _____   _____  ____  ____  _____ _    *" RESET "\n");
	printf(GREEN"* |_   |  /   ||  __||  _  |  |  _  ||  _  | |  _  ||_   ||  __||  __|| |_  *" RESET "\n");
	printf(GREEN"*  |  |  / _  || |   | | | |  | |_| || |_| | | | | |  |  || |_  | |   |  _| *" RESET "\n");
	printf(GREEN"*  |  | / |_| || |   | | | |  |  ___||  _  / | | | |  |  ||  _| | |   | |   *" RESET "\n");
	printf(GREEN"* _/  |/  / | || |__ | |_| |  | |    | | | | | |_| | _/  || |__ | |__ | |__ *" RESET "\n");
	printf(GREEN"*|___/|__/  |_||____||_____|  |_|    |_|  |_||_____||___/ |____||____||____|*" RESET "\n");
	printf(GREEN"*                                                                           *" RESET "\n");
	printf(GREEN"*        SPEECH RECOGNITION MODULE   - Developed by Q.MASCRET               *" RESET "\n");
	printf(GREEN"*****************************************************************************" RESET "\n");
	printf("\n");
	std::cout << std::left << std::setw(6) << std::setfill(' ') << GREEN "Current Mode ..is " RESET;
	std::cout << std::left << std::setw(10) << std::setfill(' ') << mode ;
	std::cout << std::endl;
	std::cout << std::left << std::setw(6) << std::setfill(' ') << GREEN "Current Word ..is " RESET ;
	std::cout << std::left << std::setw(10) << std::setfill(' ') << word ;
	std::cout << std::endl;
	std::cout << std::left << std::setw(6) << std::setfill(' ') << GREEN "Current Status is " RESET ;
	std::cout << std::left << std::setw(10) << std::setfill(' ') << status ;
	std::cout << std::endl;
}
}
}

void Result (std::queue<int> &my_queue,JacoArm *arm,jaco_joystick_axis_t axes, jaco_joystick_t buttonValue ){
	int n;
	int OldClass;
	OldClass=0;
	n=0;
	while(1){
		while(!my_queue.empty()){
		n=my_queue.front();
		my_queue.pop();
		//buttonValue = arm ->get_button_info();
		//std::cout <<*buttonValue.button << std::endl;
		}
	
		ModeCHange(arm,axes, OldClass,  n);
		OldClass=n;
	}
}


int main(){
	// queues
	std::queue<int> my_queue;
	std::system("clear");
	printf(GREEN"****************************************************************************" RESET "\n");
	printf(GREEN"*  ____    ___  ____  _____    _____  _____   _____  ____  ____  _____ _    *" RESET "\n");
	printf(GREEN"* |_   |  /   ||  __||  _  |  |  _  ||  _  | |  _  ||_   ||  __||  __|| |_  *" RESET "\n");
	printf(GREEN"*  |  |  / _  || |   | | | |  | |_| || |_| | | | | |  |  || |_  | |   |  _| *" RESET "\n");
	printf(GREEN"*  |  | / |_| || |   | | | |  |  ___||  _  / | | | |  |  ||  _| | |   | |   *" RESET "\n");
	printf(GREEN"* _/  |/  / | || |__ | |_| |  | |    | | | | | |_| | _/  || |__ | |__ | |__ *" RESET "\n");
	printf(GREEN"*|___/|__/  |_||____||_____|  |_|    |_|  |_||_____||___/ |____||____||____|*" RESET "\n");
	printf(GREEN"*                                                                           *" RESET "\n");
	printf(GREEN"*        SPEECH RECOGNITION MODULE   - Developed by Q.MASCRET               *" RESET "\n");
	printf(GREEN"*****************************************************************************" RESET "\n");
	printf("\n");

  // explicitly initialize jaco_joystick_axis_t axesa libusb context; optional
  KinDrv::init_usb();



  printf(BLUE "Create a JacoArm \n" RESET);
  JacoArm *arm;
  try {
    arm = new JacoArm();
    printf(GREEN "Successfully connected to arm! \n" RESET);
  } catch( KinDrvException &e ) {
    printf(RED "error %i: %s \n" RESET, e.error(), e.what());
    return 0;
  }

  printf(BLUE "Gaining API control over the arm \n" RESET);
  arm->start_api_ctrl();



  //check if we need to initialize arm
  jaco_retract_mode_t mode = arm->get_status();
  printf("Arm is currently in state: %i \n", mode);
  if( mode == MODE_NOINIT ) {
    //push the "HOME/RETRACT" button until arm is initialized
    jaco_joystick_button_t buttons = {0};
    buttons[2] = 1;
    arm->push_joystick_button(buttons);

    while( mode == MODE_NOINIT ) {
      usleep(1000*10); // 10 ms
      mode = arm->get_status();
    }

    arm->release_joystick();
  }

  // we want to start from home_position
  goto_home(arm);

  // need cartesian-control for joystick simulation.
  // Angular-control is also possible, then you would control each joint!
  arm->set_control_cart();
  usleep(1e6);
  // Check the documentation (or types.h) to see how to interprete the joystick-values.
  // Also make sure, that all the fields of a joystick-structs that should not have an effect are set to 0! So initialize all jaco_joystick_ structs with 0!
  jaco_joystick_axis_t axes = {0};
 // jaco_joystick_t stateJaco;
 // std::cout << *stateJaco.button << std::endl;
  jaco_joystick_t buttonValue;
/*  launch all my thread */
	std:: thread first(PythonRoutine) ;
	std:: thread third(PipeClass,arm,axes, std::ref(my_queue));
	std:: thread dd(Result,std::ref(my_queue),arm, axes,buttonValue);
	first.join();
	third.join();
	dd.join();
	return 0 ;
	
}

