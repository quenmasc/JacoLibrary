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

using namespace KinDrv;
PythonBridge Bridge ;

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
      printf("some error?! \n");
      return 0;
      break;

    case MODE_READY_STANDBY:
      printf("nothing to do here \n");
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
			case 7 :
				if(OldClass!=7){
					arm->push_joystick_button(2);
					arm->release_joystick();
				}
				break;
			case 1 :
				if(OldClass!=1){
					axes.trans_fb = 2.5;
					arm->move_joystick_axis(axes);
					usleep(2e6);
					arm->release_joystick();
			}
			break;
			case 2 :
				if(OldClass!=2){
					axes.trans_fb = -2.5;
					arm->move_joystick_axis(axes);
					usleep(2e6);
					arm->release_joystick();
			}
			break;
			case 3 :
				if(OldClass!=3){
					axes.trans_lr = 2.5;
					arm->move_joystick_axis(axes);
					usleep(2e6);
					arm->release_joystick();
				}
			break;
			case 4 :
				if(OldClass!=4){
					axes.trans_lr = -2.5;
					arm->move_joystick_axis(axes);
					usleep(2e6);
					arm->release_joystick();
				}
			break;
			default :
				OldClass=0;
				break;
	}
}


/* My THREAD */

void foo(){
	PyGILState_STATE gstate=PyGILState_Ensure();
	Bridge.Running_python();
	PyGILState_Release(gstate);
	//while(1){}
}

void fol(){
	Bridge.ClassValue2();
}

void mess(JacoArm *arm,jaco_joystick_axis_t axes){
	sleep(2);
	const char *fifo_name="/home/pi/libkindrv/examples/build/fifo";
	std::cout << "Pipe is opened" << std::endl;
	int OldClass;
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
ModeCHange(arm,axes, OldClass,  n);
OldClass=n;
}
}




int main(){
  
/* Create JACO ARM and Initialization */
  printf("Speech Recognition Module \n");

  // explicitly initialize jaco_joystick_axis_t axesa libusb context; optional
  KinDrv::init_usb();



  printf("Create a JacoArm \n");
  JacoArm *arm;
  try {
    arm = new JacoArm();
    printf("Successfully connected to arm! \n");
  } catch( KinDrvException &e ) {
    printf("error %i: %s \n", e.error(), e.what());
    return 0;
  }

  printf("Gaining API control over the arm \n");
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
  printf("Arm is initialized now, state: %i \n", mode);

  // we want to start from home_position
  goto_home(arm);

  // need cartesian-control for joystick simulation.
  // Angular-control is also possible, then you would control each joint!
  arm->set_control_cart();
  usleep(1e6);

  printf("Sending joystick movements. We want the arm to: \n");
  // Check the documentation (or types.h) to see how to interprete the joystick-values.
  // Also make sure, that all the fields of a joystick-structs that should not have an effect are set to 0! So initialize all jaco_joystick_ structs with 0!
  jaco_joystick_axis_t axes = {0};
	
	
	/* launch all my thread */
	std:: thread first(foo) ;
	std:: thread second(fol);
	std:: thread third(mess,arm,axes);
	first.join();
	second.join();
	third.join();
	return 0 ;
	
}

