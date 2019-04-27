#include "image.h"

#include "Serialcom.cpp"
#include "Motors.h"



Serialcom Ser;
Motors   Motors;

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
 /***************************************/
void setup() 
{
    Serial.begin(115200);
    Motors.init();
}


void processCommand(int curcom)
{  // COMMANDS TO BE PROCESSED 
   // COMMANDS <"HOME" = 1, "START" = 2, "PAUSE" = 3, "CANCEL" =4, "MMOV" = 5, "0" = INITIAL COMMAND[DO NOTHING&WAIT] >

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
      
     lastCommand =0;
   }
   else if(curcom ==5)
   {
     //get ser msg
     ManualControl(); 
   }
   
}

void getStrtPt(){
   int stepx_pre_pixel = 7;
  start_imgX = int( (XBED_IN_PIX/2) - int(ROWS/2) );  //STILL IN PIXELS
  start_imgY = int( (YBED_IN_PIX_IN_PIX/2) - ((COLS *8)/2) ); //START IN PIXELS

  start_imgX = start_imgX * stepx_pre_pixel;  // start_imgX in steps steps
  start_imgY = int( (start_imgY * 137.1) /11);   // start_imgY in steps > pixels x resol 137.1 microns / step size 9.375 //CHANGED CHANGED CHANGED 9.375 > 11
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
      P_calibrat = Motors.Calibrate_ref_bed();
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
    else
    {
      if(counter_stepX < start_imgX)
      {
          Motors.StepX(XAWAYDIR);  
          counter_stepX = counter_stepX +1;
      }
      if(counter_stepY <start_imgY)
      {
            Motors.StepY(YHOMEDIR); //CHANGED CHANGED CHANGED
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
      totalpass = COLS/16;
      Singlepass =0;
      counter_stepX =0;
      counter_stepY =0;
      Print_strt_flag = true;
     
    }
    if(paused == true)
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
    else
    {
      
      if( Singlepass < totalpass)
      {
        
        if(return_to_row1 == false)
        {
          
          if(counter_stepX < ROWS)
             {  
               
               //here it prints
               //Xaar.print();
              // delayMicroseconds(300);
               for(int i =0; i <7;i++)  //travel one pixel and prints per time
               {
                Motors.StepX(XAWAYDIR);
               }
               counter_stepX = counter_stepX +1;
             }
             
          else if(counter_stepX == ROWS)
            {
              int stepy_per_pass = 1563;
              Singlepass = Singlepass +1;
              counter_stepY = stepy_per_pass;
              return_to_row1 = true;
            }
             
      }
      else if (return_to_row1 == true)
      {
         if(counter_stepX >0 )
           {
             for(int i =0; i <7;i++)  //return one pixel  per time
               {
                delayMicroseconds(50);
                Motors.StepX(XHOMEDIR);
               }
               
             counter_stepX = counter_stepX -1;
           }
         if(counter_stepY >0)
         {
            Motors.StepY(YHOMEDIR);  //CHANGED
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
           Serial.println("FINISHED");
      }
    }
//    flag lel paused true, get data , false continue
//    counter_stepx where in rows +1
//    single pass = which cols 
//    locationx = getstepsx 
//    locationy = getstepsy
   
   }
}

void ManualControl()
{
    int *motiondata = Ser.getMMove();
    boolean stopxx = false;
    boolean stopyy = false;

      if(Motors.isEnabled() == false){
          Motors._enable();
      }
    
      if(*(motiondata) ==1)       //1 AWAY
      {
        if(Motors.GetStepX() < MAXSTEPX -2)
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
        if(Motors.GetStepY() < MAXSTEPY -2)
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
        Serial.println("AXES LIMITS REACHED");
        lastCommand =0;
      }
      else if(stopxx == true && stopyy == false)
      {
        Ser.set_MMove(0,*(motiondata+1));
      }
      else if(stopxx == false && stopyy == true)
      {
        Ser.set_MMove(*(motiondata),0);
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
        processCommand(currentCommand);
        lastCommand = currentCommand;
        Serial.println(currentCommand);
        Ser.start();
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
