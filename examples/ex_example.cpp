#include <iostream>
#include <sstream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <libkindrv/kindrv.h>
#include <sys/select.h>

using namespace KinDrv;

ModeChange CM;
int c;
int newclassLabel;
int OldClass=0;
bool flag=1;
jaco_joystick_axis_t axes = {0};
JacoArm *arm;
int i=0;
int counter=0;
int test=0;
// keyboard 
struct termios orig_termios;

void reset_terminal_mode()
{
    tcsetattr(0, TCSANOW, &orig_termios);
}
void set_conio_terminal_mode()
{
    struct termios new_termios;

    /* take two copies - one for now, one for later */
    tcgetattr(0, &orig_termios);
    memcpy(&new_termios, &orig_termios, sizeof(new_termios));

    /* register cleanup handler, and set the new terminal mode */
    atexit(reset_terminal_mode);
    cfmakeraw(&new_termios);
    tcsetattr(0, TCSANOW, &new_termios);
}
int kbhit()
{

    struct timeval tv = { 0L, 0L };
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return select(1, &fds, NULL, NULL, &tv);
}

int getch()
{
    int r;
    unsigned char c;
    if ((r = read(0, &c, sizeof(c))) < 0) {
        return r;
    } else {
        return c;
    }
}
//
void ModChange(int classLabel,int OldClass,JacoArm *arm){
		//printf("Old class %c",OldClass);
		switch (classLabel){
			/*case 1 :
				if(OldClass!=1){
					arm->push_joystick_button(2);
					arm->release_joystick();
				}*/
			case 2 :
				if(OldClass!=2){
					arm->push_joystick_button(7);
					arm->release_joystick();
				}
				break;
			
			case 3 :
				if(OldClass!=3){
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
					break;
				}
			case 4 :
				if(OldClass!=4){
					arm->push_joystick_button(2);
					arm->release_joystick();
				}
			default :
				OldClass=0;
	}
}
void MovementMode(int classLabel,bool flag, jaco_joystick_axis_t axes,JacoArm *arm){
	switch (classLabel){
			case 1 :
						axes.trans_fb = -2.5;
						arm->move_joystick_axis(axes);
						break;
						//arm->release_joystick();
			case 2 :
						axes.trans_fb = 2.5;
						arm->move_joystick_axis(axes);
						break;
						//arm->release_joystick();
			case 3 :
						//printf("value : %f.",axes.trans_lr);
						axes.trans_lr=2.5f;
						arm->move_joystick_axis(axes);
						break;
			case 4 :
						axes.trans_lr=-2.5f;
						arm->move_joystick_axis(axes);
						break;
			default :
				break;
		}
		//axes.trans_fb = 0.f;
		arm->move_joystick_axis(axes);
		usleep(1e6);
		//arm->release_joystick();
}
// goto arm
int goto_home(JacoArm *arm)
{
  // going to HOME position is possible from all positions. Only problem is,
  // if there is some kinfo of error
  jaco_retract_mode_t mode = arm->get_status();
  switch( mode ) {
    case MODE_RETRACT_TO_READY:
      // is currently on the way to HOME. Need 2 button presses,
      // 1st moves towards RETRACT, 2nd brings it back to its way to HOME
      arm->push_joystick_button(2);
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

// int main
int main(){
	while(1){
		c=0;
		set_conio_terminal_mode();
		if (kbhit()){
			c=getch();
			
		}
		reset_terminal_mode();
		// keyboard
		if (c==3){
				KinDrv::close_usb();
				break;
		}
		if (c==32){
					i=1;
					KinDrv::init_usb();
					printf("Create a JacoArm \n");
					
					try {
						arm = new JacoArm();
						printf("Successfully connected to JACO arm! \n");
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
					
					arm->set_control_cart();
					usleep(1e6);
					printf("Sending joystick movements. We want the arm to: \n");
					// Check the documentation (or types.h) to see how to interprete the joystick-values.
					// Also make sure, that all the fields of a joystick-structs that should not have an effect are set to 0! So initialize all jaco_joystick_ structs with 0!
					
		}
		
		if (i==1){
			test=0;
			if (c==100){
				test=1;
				}
			if (c==102){
				test=2;
				}
			if (c==111){
				test=3;
			}
			if (c==112){
				test=4;
			}
			if (c==122){
				test=6;
			}
			
			
			newclassLabel=CM.classPCA(test);
	//	printf("class is %d",newclassLabel);
			ModChange(newclassLabel,OldClass,arm);
			MovementMode(test,flag,axes,arm);
			OldClass=newclassLabel;
	}
		
		
	}
	return 0;
}
