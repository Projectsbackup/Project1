


#include "Arduino.h"

#ifndef MOTORS_H_
#define MOTORS_H_



#ifdef ARDUINO_AVR_MEGA2560

// PINS FOR THE MOTORS 

#define x_min_endstop         3
#define pin_enable_motor_x    38
#define pin_motor_step_x      A0
#define pin_direction_x       A1

#define y_min_endstop         14
#define y_motor_enable        A2
#define y_motor_step          A6
#define y_motor_dir           A7

#endif

// Maxsteps in x & y should be 16000 + Bedxsteps ref or bedystepsref...
#define MAXSTEPX      19095        // 150MM BED WIDTH / STEP RESOLUTION OF 9.375 MICRONS FROM START REF. POINT ON BED  (150000 MICRONS/9.375), MICROSTEP OF MOTOR IS 1/16 , 16000 + 3095
#define MAXSTEPY      20000        // CAN BE CHANGED AT ANYTIME DEPEND ON BED SIZE , WAS 16000

#define XHOMEDIR       1
#define XAWAYDIR       0

#define YHOMEDIR       0
#define YAWAYDIR       1

#define BED_XSTEPS_REF 3059
#define BED_YSTEPS_REF 17391

#define XBED_IN_PIX    1937     //  (stepx_pre_pixel * INT ( (150 MM * DPI(338 or 360)/25.4) /stepx_pre_pixel) )  1992 * 75 microns per pixel  149.4 mm
//#define YBED_IN_PIX_IN_PASS    2048     // INT(150 MM / (STEPY_PER_PASS_960 OR 1856 * STEPY_9.375)) * 128 PIXEL OF NOZZLES OF PRINTHEAD  EQUAL TO 14.4 CM 
#define YBED_IN_PIX_IN_PIX    1094   //when printhead is not tilted (resolution is 137.1 microns or 185dpi) & 2142 pixel in 360 dpi
/*...................................................*/

class Motors
{


  public:

    int stepX = 0;
    int stepY = 0;
    // old stepx_pre_pixel is 8, 75 microns per pixel / 9.375 , new is 19 teeth 23.4 per step total of 3 steps per pixel, microstepping is 1/8
    int stepx_pre_pixel = 7;        // Current Setup DPI is 360 and with resolution of 75 microns in X axis = 75/9.375 = 8 steps , variables that can be changed
    int stepy_per_pass = 1563;      // length of current nozzles in printhead is 17.4 mm == 17.4*1000/9.375 = 1856 steps , 17.2/11 =1563
    //step_per_pass old was 1856 , new is 960 > 9 mm vertical tilted 31 xaar / 9.375 microns
    int CurrentStepX = 0;
    
    //   for calculation of total steps in X for single pass = stepsx_pre_pixel * total rows in the image data ,
    //   current step from home meaning subtracted - from calibraiton ref steps from home to get current row
    
    int CurrentStepY = 0;      // for total of single passes per layer = currentstepsY - calibration ref point / stepy_per_pass

    boolean MotorsEnabled = false;    
    // to be added in firmware int startpointx, strtpty, endptx, endpty, currpass, totalpass
    Motors();      //Empty Constructor
    void init();
    void _enable();
    bool isEnabled();
    void _disable();
    void Homing();
    bool isHomed();


    void StepX(int dirX1);  // return remaining steps to go in X
    void StepY(int dirY1); // retrun remaining steps to go in Y
   
     
    bool Calibrate_ref_bed();     //return true if motors reached ref points 
    int GetStepX();
    int GetStepY();
    void update_StepX(int dirxx);
    void update_StepY(int diryy); // increment or decrement total stepy depend on direction.

   /*
    * ***************************************************************************
    * OLD FUNCTIONS:
    *   void StepX(int SX1,int dirX1);  // return remaining steps to go in X
    *   void StepY(int SY1,int dirY1); // retrun remaining steps to go in Y
    *    
    *   void MoveSteps(int SX, int dirX, int SY, int dirY);
    *   void Calibrate_ref_bed();     //return true if motors reached ref points      
    ****************************************************************************
    */








};

#endif
