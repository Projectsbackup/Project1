#include "image.h"

#include "printparameters.h"

#include "Serialcom.cpp"
#include "Motors.h"

#include "xaar128.h"

// CHANGES HAPPENED IN FIRMWARE AND MOTOR CLASS, IN CALIBRATION FCN AND STEP AS WELL...
// MODIFIED : getStrtPt(),START PRINTING , MANUAL CONTROL , MOTOR.CALIBRATION(), FCNS ADDED: INIT_PARAMETERS() AND ADD TO SETUP() FCN, Pause_return(), Xstep_perPixel(), Ystep_perPixel() ,..
// .. Xbed_inPixel(), Ybed_inPixel(), MaxStepX(), MaxStepY(), CalibrateXinSteps(), CalibrateYinSteps()

Serialcom Ser;
Motors   Motors;
Xaar128 xaar128;
/* SYSTEM VARIBLES */ 

 int lastCommand =0;
 boolean MMotorMove = false;    //CHECK IN MANUAL CONTROL IF MOTORS ARE STOPPED OR MOVING
 //boolean Cancel = false;
 boolean P_HOMEE = false;
 boolean P_calibrat = false;
 boolean P_Strt_DataPt = false;
 boolean P_start_flag = false;
 boolean Print_strt_flag = false;

 boolean paused = false;
 boolean return_to_row1 = false;
 
 int start_imgX =0;
 int start_imgY =0;
 int counter_stepX =0;
 int counter_stepY =0;
 int totalpass = 0;
 int Singlepass = 0;

 int lastP_locationx = 0; 
 int lastP_locationy = 0;

 boolean Printhead_PoweredON = false;
 /***************************************/
void setup() 
{
    Serial.begin(115200);
    Motors.init();
    init_Parameters();
    xaar128.init();

   // Setting up 1 MHz Square Wave for XAAR STATE MACHINE CLK //
   // TIMER1 & PIN 11 ON ATMEGA2560 
   TCCR1A = _BV(COM1A0);  // TOGGLE OC1A ON COMPARE MATCH REGISTER
   OCR1A =7;             // TOP VALUE FOR COUNTER

   TCCR1B = _BV(WGM12) | _BV(CS10);  // SELECTING CTC MODE , PRESCALER CLOCK/1
}

void init_Parameters()
{
  Serial.println("Xaar128 Printing Firmware v0.1");
  if(StepPrintPixel ==1)
  {
    int Xspd = CalculateXspd();
    
    Motors.XSetMotorSpd( Xspd );
    int xout = ((motorXResln)*1000) / Xspd;
    Serial.println("Motion Settings:");
   Serial.println("X Resolution:" + String(motorXResln) +"," + " X MotorSpd:" + String(xout) +"mm/sec");
  }
  else
  {
    int PixelResln = int((25.4/dpiX) * 1000) / StepPrintPixel;
    //Serial.println(PixelResln);
    int XmotorMove_inSteps = int(PixelResln/motorXResln);  // maybe ceil ?
    int stepDuration = int(StepPrintduration/XmotorMove_inSteps);
    //Serial.println(XmotorMove_inSteps);
    if( stepDuration < 40)
    {
      stepDuration = 40;    // Single low minimium duration is 40 microSeconds due to hardware (motor Signals) requirements
    }
    Motors.XSetMotorSpd(stepDuration);
    Serial.println("Motion Settings:");
   Serial.println("X Resolution:" + String(motorXResln) +"," + " X MotorSpd:" + String((motorXResln*1000) /stepDuration) +"mm/sec" );
  }
   int Yspd = CalculateYspd();
   Motors.YSetMotorSpd( Yspd);
   int yout = ((motorYResln)*1000) / Yspd;
  Serial.println("Y Resolution:" + String(motorXResln) +"," + " Y MotorSpd:" + String(yout) +"mm/sec");
  //Serial.println("Xstep_perPixel" + String(Xstep_perPixel()) +", Ystep_perPixel:" + String(Ystep_perPixel()) );
  //Serial.println("Xbed_inPixel" + String(Xbed_inPixel()) +", Ybed_inPixel:" + String(Ybed_inPixel()) );
  //Serial.println("CalibrateXinSteps" + String(CalibrateXinSteps()) +", CalibrateYinSteps:" + String(CalibrateXinSteps()) );
  //Serial.println("MaxStepX" + String(MaxStepX()) +", MaxStepY:" + String(MaxStepX()) );
}

void processCommand(int curcom)
{  // COMMANDS TO BE PROCESSED 
   // COMMANDS <"HOME" = 1, "START" = 2, "PAUSE" = 3, "CANCEL" =4, "MMOV" = 5, TEST_PRINTHEAD =7, "0" = INITIAL COMMAND[DO NOTHING&WAIT] >

   if(curcom ==0)
   {
    
   }
   
   else if(curcom ==1)
   {
      if(Motors.isEnabled()== false)
      {
         Motors._enable();
      }
      if(Motors.isHomed() == false)
      {
        Motors.Homing();
      }
      else if(Motors.isHomed() == true)
      {
        //send msg that motors are homed
      }
   }

   else if(curcom ==2)
   {
        if(Motors.isEnabled()== false)
          {
            Motors._enable();
          }

        if(Printhead_PoweredON == false)
          {
            xaar128.powerUp();
            Printhead_PoweredON = true;
          }
        
        StartPrinting();
       
   }

   else if(curcom ==3)
   {
      // WAITS 
      //set & get last stepx,stepy,row,col
      //setPrintPos_data(); 
      lastP_locationx = Motors.GetStepX();
      lastP_locationy = Motors.GetStepY();
      paused = true;
   }

   else if(curcom ==4)
   {
      Motors._disable();
      // Xaar.powerdown();

      P_HOMEE = false;
      P_calibrat = false;
      P_Strt_DataPt = false;
      
      P_start_flag = false;
      Print_strt_flag = false;
      paused = false;
      return_to_row1 = false;

      if(Printhead_PoweredON == true)
      {
        xaar128.powerDown();
        Printhead_PoweredON = false;
      }
      
     lastCommand =0;
   }
   else if(curcom ==5)
   {
     //get ser msg
     ManualControl(); 
   }

   else if(curcom ==7)
   {
     //get ser msg
    PrintHeadTest(); 
   }
   
}

void Pause_return()
{
  if(Motors.GetStepX() < lastP_locationx)
        {
          Motors.StepX(XAWAYDIR);
        }
        else if(Motors.GetStepX() > lastP_locationx){
          Motors.StepX(XHOMEDIR);
        }

        if(Motors.GetStepY() < lastP_locationy)
        {
          Motors.StepY(YAWAYDIR);
        }
        else if(Motors.GetStepY() > lastP_locationy){
          Motors.StepY(YHOMEDIR);
        }
        if( (Motors.GetStepX() == lastP_locationx) && (Motors.GetStepY() == lastP_locationy) )
        {
          paused = false;
        }        
}
int Xstep_perPixel()
{
  int pixel_in_microns = (25.4*1000) /dpiX;
  int stepx_perPixel = int(pixel_in_microns/motorXResln);
  return stepx_perPixel;
}

int  Ystep_perPixel()
{
  int Ypixel_in_microns = (25.4 *1000) /dpiY;
  int stepy_perPixel = int(Ypixel_in_microns/motorYResln);
  return stepy_perPixel;
}

int Xbed_inPixel()
{
  int Xbed_inPix = int ( (long(BedsizeX) * (long)dpiX)/25.4);
  return Xbed_inPix;
}

int Ybed_inPixel()
{
  int Ybed_inPix = int ( (long(BedsizeY) * long(dpiY))/25.4);
  return Ybed_inPix;
}

int MaxStepX()
{
  int maxStepx = int( (long(BedsizeX + CalibX) /motorXResln) * 1000);
  return maxStepx;
}
int MaxStepY()
{
  int maxStepy = int( (long(BedsizeY + CalibY) /motorYResln) * 1000);
  return maxStepy;
}

int CalibrateXinSteps()
{
  int CalibXsteps = int( (long(CalibX) *1000)/motorXResln);
  return CalibXsteps;
}

int CalibrateYinsteps()
{
  int CalibYsteps = int( (long(CalibY) *1000)/motorYResln);
  return CalibYsteps;
}

int CalculateXspd()
{
  if(motorXspd == 0)
  {
    int TimePerStep = 40;
    return TimePerStep;
  }
  int TimePerStep = int( (1000/motorXspd)* motorXResln);
  if(TimePerStep <40)
  {
      TimePerStep = 40;
  }
  return TimePerStep;
}

int CalculateYspd()
{
  if(motorYspd == 0)
  {
    int TimePerStepY = 40;
    return TimePerStepY;
  }
  int TimePerStepY = int( (1000/motorYspd)* motorYResln);
  if(TimePerStepY <40)
  {
      TimePerStepY = 40;
  }
  return TimePerStepY;
}


void Jet(int currentSinglePass, int currentRow)   // any expectations to this function like motorResln is higher than step required in print phase of single Print command is handled in Host Software Program..
{
  int XstepPerDot = Xstep_perPixel();
  if(StepPrintPixel == 1)
   {
     xaar128.PRINT(currentSinglePass,currentRow,0);
    if(motorXspd !=0)
    {
     int Xduration_per_step = CalculateXspd(); // -1 means Max speed of Motor
     Motors.XSetMotorSpd(Xduration_per_step);
    }
    else
    {
      
       Motors.XSetMotorSpd(-1);
    }
     for(int i =0; i <XstepPerDot;i++)  //travel one pixel and prints per time  //change to v0.2
       {
        Motors.StepX(XPrintDirection);
       } 
   }
   else
   {
    int PixelResln = int((25.4/dpiX) * 1000) / StepPrintPixel;
    int XmotorMove_inSteps = int(PixelResln/motorXResln);
    int stepDuration = int(StepPrintduration/XmotorMove_inSteps);
    if( stepDuration < 40)
    {
      stepDuration = 40;    // Single low minimium duration is 40 microSeconds due to hardware (motor Signals) requirements
    }
    Motors.XSetMotorSpd(stepDuration);
    xaar128.PRINT(currentSinglePass, currentRow,1);
    for(int i =0; i <XstepPerDot;i++)  //travel one pixel and prints per time  //change to v0.2
       {
        Motors.StepX(XPrintDirection);
       }  
   }
}

void getStrtPt()
{
   int stepx_pre_pixel = Xstep_perPixel();
  start_imgX = int( (Xbed_inPixel()/2) - int(ROWS/2) );  //STILL IN PIXELS
  start_imgY = int( (Ybed_inPixel()/2) - ((COLS *8)/2) ); //START IN PIXELS

  start_imgX = start_imgX * stepx_pre_pixel;  // start_imgX in steps steps
  start_imgY = int( start_imgY * Ystep_perPixel() );   // start_imgY in steps > pixels x resol 137.1 microns / step size 9.375 //CHANGED CHANGED CHANGED 9.375 > 11
  //IMAGEROW
}
void StartPrinting()
{
   if(P_HOMEE == false)
   {
     if(Motors.isHomed() == false)
     {
      Motors.Homing();
     }
     else
     {
      P_HOMEE = true;
     }
   }
   else if(P_HOMEE == true && P_calibrat == false)
   {
      P_calibrat = Motors.Calibrate_ref_bed(CalibrateXinSteps(),CalibrateYinsteps()); //changed v0.2, was empty function ()
   }
   else if (P_HOMEE == true && P_calibrat == true && P_Strt_DataPt == false)
   {
    //Move to strpt 
      if(P_start_flag == false)
      { 
        paused = false;
        counter_stepX =0;
        counter_stepY =0;
        getStrtPt();
        delayMicroseconds(100);
        P_start_flag = true;
      }

       if(paused == true)
    {
        Pause_return();
      
    }
    else
    {
      if(counter_stepX < start_imgX)
      {
          Motors.StepX(XPrintDirection);  //changed v0.2, was XAWAYDIR
          counter_stepX = counter_stepX +1;
      }
      if(counter_stepY <start_imgY)
      {
            Motors.StepY(YPrintDirection); //CHANGED v0.2 CHANGED CHANGED, WAS YHOMEDIR
            counter_stepY = counter_stepY +1;  
            
      }
      if(counter_stepX == start_imgX && counter_stepY == start_imgY)
      {
         
         P_Strt_DataPt = true;
      }
    }
   }
   else if (P_HOMEE == true && P_calibrat == true && P_Strt_DataPt == true) // here start printing
   { 
    
    if(Print_strt_flag == false){
      paused = false;
      totalpass = COLS/16;    // totalpass * num_ofnozzles = cols*8{bits_in_byte} , cols already /8 to form 1 byte each and 8*16 = 128 so > cols_divided_already/16 = single_pass
      Singlepass =0;
      counter_stepX =0;
      counter_stepY =0;
      Print_strt_flag = true;
     
    }
    if(paused == true)
    {
        Pause_return();
    }
    else
    {
      
      if( Singlepass < totalpass)
      {
        
        if(return_to_row1 == false)
        {
          
          if(counter_stepX < ROWS)
             {  
              //Counter_stepX represents current Row from total ROWS
               
//               //here it prints
//               //Xaar.print();
//              // delayMicroseconds(300);
//               for(int i =0; i <7;i++)  //travel one pixel and prints per time  //change to v0.2
//               {
//                Motors.StepX(XPrintDirection);
//               }
               Jet(Singlepass,counter_stepX);
               counter_stepX = counter_stepX +1;
             }
             
          else if(counter_stepX == ROWS)
            {
              int stepy_per_pass = int( (singlepassDim/motorYResln)*1000);  //need to be changed to v0.2, was 1563 = (17.2_mm{singlepassdim}/11_microns)*1000
              Singlepass = Singlepass +1;
              counter_stepY = stepy_per_pass;
              return_to_row1 = true;
            }
             
      }
      else if (return_to_row1 == true)
      {
         if(counter_stepX >0 )
           {
            int __XSteps = Xstep_perPixel();
             for(int i =0; i <__XSteps;i++)  //return one pixel  per time
               {
                delayMicroseconds(50);        // NECESSARY AT HIGH SPEEDS [ LIMITS OF MOTOR HARDWARE SIGNALS TO GIVE EMPTY TIME FOR MOTOR TO INVERSE ITS DIRECTION..
                Motors.StepX(XPrint_return);  //changed to v0.2 was XHOMEDIR
               }
               
             counter_stepX = counter_stepX -1;
           }
         if(counter_stepY >0)
         {
            Motors.StepY(YPrintDirection);  //CHANGED
            counter_stepY = counter_stepY -1;
         }
         if( (counter_stepX ==0) && (counter_stepY ==0) )
           {
              return_to_row1 = false; 
           }
      }
      }
      else 
      {
           lastCommand = 0; //finished and back home
           if(Printhead_PoweredON == true)
            {
                xaar128.powerDown();
                Printhead_PoweredON = false;
            }
           Serial.println("<FINISHED PRINTING A LAYER>");
      }
    }
//    flag lel paused true, get data , false continue
//    counter_stepx where in rows +1
//    single pass = which cols 
//    locationx = getstepsx 
//    locationy = getstepsy
   
   }
}

void ManualControl()   //CHANGED v0.2, was MAXSTEPX, MAXSTEPY INSTEAD OF MaxStep_X and MaxStep_Y
{
    int *motiondata = Ser.getMMove();
    boolean stopxx = false;
    boolean stopyy = false;

    int MaxStep_X  = MaxStepX();
    int MaxStep_Y  = MaxStepY();

      if(Motors.isEnabled() == false){
          Motors._enable();
      }
    
      if(*(motiondata) ==1)       //1 AWAY
      {
        if(Motors.GetStepX() < MaxStep_X -2)
        {
          Motors.StepX(XAWAYDIR);
        }
        else
        {
          stopxx = true;
        }
        
      
        
      }
      else if(*(motiondata) ==-1)  //-1 XHOME
      {
        if(Motors.GetStepX() > 2)
        {
        Motors.StepX(XHOMEDIR);
        }
        else
        {
          stopxx = true;
        }
      }

      if(*(motiondata +1) ==1)   //1 Y AWAY 
      {
        if(Motors.GetStepY() < MaxStep_Y -2)   
        {
        Motors.StepY(YAWAYDIR);
        }
        else
        {
          stopyy = true;
        }
      }
      else if(*(motiondata+1) ==-1)   // -1 YHOME
      {
        if(Motors.GetStepY() > 2)
        {
        Motors.StepY(YHOMEDIR);
        }
        else
        {
          stopyy = true;
        }
      }

      if(stopxx == true && stopyy == true)
      {
        Ser.set_MMove(0,0);
        // send msg
        Serial.println("<AXES LIMITS REACHED>");
        lastCommand =0;
      }
      else if(stopxx == true && stopyy == false)
      {
        Ser.set_MMove(0,*(motiondata+1));
        Serial.println("<X-AXIS LIMITS REACHED>");
      }
      else if(stopxx == false && stopyy == true)
      {
        Ser.set_MMove(*(motiondata),0);
        Serial.println("<Y-AXIS LIMITS REACHED>");
      }
        
}
void PrintHeadTest()
{
  if(Printhead_PoweredON == false)
     {
      xaar128.powerUp();
      Printhead_PoweredON = true;
     }
     
  xaar128.Test();
  
  xaar128.powerDown();
  Printhead_PoweredON = false;
  
}
void ManualSpeedCheck(int lastcom,int crrntCommand)
{
  if( crrntCommand == 5)
  {
    Motors.XSetMotorSpd(1020);
    Motors.YSetMotorSpd(1020);
  }
  else
  {
    if( (lastcom == 5) && (lastcom != crrntCommand) )
    {
      init_Parameters();
    }
  }
}

void Update()
{
 
   if(!Ser.checkConnection())
   {
    
     // Xaar.powerdown();
     
     Motors._disable();
     //Serial.println("TEST");
      
    }
    else if(Ser.checkConnection())
    {
      
      if(Ser.checkdata())
        {
        
        int currentCommand = Ser.getCommand();
        if(currentCommand == -1)
        {
          processCommand(lastCommand);  
        }
        else
        {
        ManualSpeedCheck(lastCommand,currentCommand);
        processCommand(currentCommand);
        lastCommand = currentCommand;
        Serial.println(currentCommand);
        //Ser.start();
        }
        }
      else
      {
       
        processCommand(lastCommand);
        
      }
      
    }
}

void loop() {
  
   Update();
    
}
