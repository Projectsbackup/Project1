/*
 * THIS CLASS IS RESPONSIBLE FOR CONTROLLING MOTOR MOTION
 * AS A PART OF 2D KINEMATICS MODULE FOR TESTING PRINTHEAD
 * ON 2D TEST RIG SYSTEM
 * 
 */


#include "Arduino.h"
#include "Motors.h"

Motors::Motors(){}   //CONSTRUCTOR FOR MOTOR CLASS

void Motors::init()
  {
     pinMode(x_min_endstop,INPUT_PULLUP);  // END-STOP SWITCH/SENSOR IS LOW WHEN PRESSED OR MOTOR IS HOMED
     pinMode(pin_enable_motor_x,OUTPUT);
     pinMode(pin_direction_x,OUTPUT);
     pinMode(pin_motor_step_x,OUTPUT);
    
     pinMode(y_min_endstop,INPUT_PULLUP);
    
     pinMode(y_motor_enable,OUTPUT);
     pinMode(y_motor_dir,OUTPUT);
     pinMode(y_motor_step,OUTPUT);
    
     //MOTOR IS ENABLED WHEN LOW [ACTIVE LOW]
     digitalWrite(pin_enable_motor_x,HIGH);
    
     digitalWrite(y_motor_enable,HIGH);

  
  }

 void Motors::_enable()
 {
   digitalWrite(pin_enable_motor_x,LOW);

   digitalWrite(y_motor_enable,LOW);
   MotorsEnabled = true;
  
 }


 bool Motors::isEnabled()
 {
  return MotorsEnabled;
 }

 void Motors::_disable()
 {
  digitalWrite(pin_enable_motor_x,HIGH);

  digitalWrite(y_motor_enable,HIGH);
  MotorsEnabled = false;
 }

 void Motors::Homing()
 {
    if(isHomed() == false)
    {
        if((digitalRead(x_min_endstop) == true) && (digitalRead(y_min_endstop) == true))
          {
                StepX(XHOMEDIR);
                StepY(YHOMEDIR);
          }
          else if((digitalRead(x_min_endstop) == true) && (digitalRead(y_min_endstop) == false))
          {
              StepX(XHOMEDIR);
          }
          else if((digitalRead(x_min_endstop) == false) && (digitalRead(y_min_endstop) == true))
          {
             StepY(YHOMEDIR);
          }
          
    }
  
 }


bool Motors::isHomed()
{
    if( (digitalRead(x_min_endstop) == false) && (digitalRead(y_min_endstop) == false) ) 
      {
           return true;
      }
    else 
      {
           return false;
      }
}


 void Motors::StepX(int dirX1)
 {
      if( isEnabled() )    // && GetStepX() < MAXSTEPX
      {
        digitalWrite(pin_direction_x,dirX1);
        digitalWrite(pin_motor_step_x,HIGH);
        
        delayMicroseconds(20);    //WORKING DELAYS 20 & 20 AFTER LOW
        
        digitalWrite(pin_motor_step_x,LOW);
        delayMicroseconds(1000);
        update_StepX(dirX1);
      }
      
 }
    
    
void Motors::StepY(int dirY1)
{
     if( isEnabled()  )   //&& GetStepY() < MAXSTEPY
      {
         digitalWrite(y_motor_dir,dirY1);
         digitalWrite(y_motor_step,HIGH);
         
         delayMicroseconds(20);
         
         digitalWrite(y_motor_step,LOW);
         delayMicroseconds(1000);   // IT WAS 80 
         update_StepY(dirY1);
      }
  
}


bool Motors::Calibrate_ref_bed()
{
    if( GetStepX() < BED_XSTEPS_REF )
    {
      StepX(XAWAYDIR);
    }
    else if( GetStepX() > BED_XSTEPS_REF )
    {
      StepX(XHOMEDIR);
    }
    if( GetStepY() < BED_YSTEPS_REF )
    {
      StepY(YAWAYDIR);
    }

    else if( GetStepY() > BED_YSTEPS_REF )
    {
      StepY(YHOMEDIR);
    }
    
    if((GetStepX() == BED_XSTEPS_REF) && (GetStepY() == BED_YSTEPS_REF) )
    {
       return true; 
    }

    return false;
}

 int Motors::GetStepX()
 {
    return CurrentStepX;
 }

 int Motors::GetStepY()
 {
   return CurrentStepY;
 }


 void Motors::update_StepX(int dirxx)
 {
    if(dirxx == XHOMEDIR)
    {
      CurrentStepX = CurrentStepX - 1;
    }

    if(dirxx == XAWAYDIR)
    {
      CurrentStepX = CurrentStepX + 1;
    }

    if(CurrentStepX <0)
    {
      CurrentStepX =0;
    }
  
 }


 void Motors::update_StepY(int diryy)
 {
    if(diryy == YHOMEDIR)
    {
      CurrentStepY = CurrentStepY - 1;
    }

    if(diryy == YAWAYDIR)
    {
      CurrentStepY = CurrentStepY + 1;
    }
    
    if(CurrentStepY <0)
    {
      CurrentStepY =0;
    }
    
 }

 
