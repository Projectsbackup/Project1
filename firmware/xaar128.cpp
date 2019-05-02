#include <SPI.h>
#include "xaar128.h"
#include "image.h"
#include "Arduino.h"

Xaar128::Xaar128() {}

void Xaar128::init () {

  // 12 PINS TO DEFINE

  pinMode(nSS1, OUTPUT);
  pinMode(nSS2, OUTPUT);

  pinMode(nCLK, OUTPUT);
  pinMode(SCK, OUTPUT);

  pinMode(nRESET, OUTPUT);
  pinMode(xVDD, OUTPUT);

  pinMode(nFIRE, OUTPUT);
  pinMode(MOSI, OUTPUT);

  pinMode(relayVHCH, OUTPUT);
  digitalWrite(relayVHCH, LOW);

  pinMode(relayVHCL, OUTPUT);
  digitalWrite(relayVHCL, LOW);

  pinMode(READY, INPUT);
  pinMode(MISO, INPUT);

  // SPI COMMUNICATION: DATA IS CLOCKED INTO THE SHIFT REGISTER ON THE LEADING EDGE
  // OF SCK AND CLOCKED OUT ON THE FALLING EDGE OF THE SCK
  // CLOCK IDLE IS HIGH ( PAGE 33)
  SPI.setDataMode(SPI_MODE2);
  // XAAR SPI CLOCK SPEED MUST BE 1 MHZ
  SPI.setClockDivider(SPI_CLOCK_DIV16);
  SPI.begin();

  // Set initial State for nFIRE
  digitalWrite(nFIRE, HIGH);

  // Chip Select disable (When HIGH)
  digitalWrite(nSS2, HIGH);
  digitalWrite(nSS1, HIGH);

  // RESET ACTIVE WHEN LOW, SET INACTIVE
  digitalWrite(nRESET, HIGH);

  // SET LOGIC VOLT LOW FIRST
  digitalWrite(xVDD, LOW);
  readyState = LOW;

  delay(10);

}


void Xaar128::powerUp() {

  //Enable VDD HIGH
  digitalWrite(xVDD, HIGH);
  delay(50);

  // nRESET pulse width = 500 ns
  // nRESET : Active low, asynchronous reset of the driver chip sequence logic, 
  // nRESET will not reset the contents of the input data shift registers.
  digitalWrite(nRESET, LOW);
  delayMicroseconds(1);

  digitalWrite(relayVHCH, HIGH);
  delay(50);
  digitalWrite(relayVHCL, HIGH);
  delay(50);

  digitalWrite(nRESET, HIGH);
  delay(10);
}

void Xaar128::powerDown(){

  digitalWrite(nRESET,HIGH);
  delayMicroseconds(1);

  digitalWrite(nRESET,LOW);
  delay(50);

  digitalWrite(relayVHCH,LOW);
  delay(50);
  digitalWrite(relayVHCL,LOW);

  digitalWrite(nRESET,HIGH);

  digitalWrite(xVDD,LOW);
  
}

void Xaar128::Test()
{
  byte T[64] = {0b11111111,0b11111111,0b11111111,0b11111111,0b11111111,0b11111111,0b11111111,0b11111111};

  digitalWrite(nSS2,LOW);
  digitalWrite(nSS1,HIGH);
  this->loadBuffer64(T);

  digitalWrite(nSS2,HIGH);
  digitalWrite(nSS1,LOW);
  this->loadBuffer64(T);

  digitalWrite(nSS1,HIGH); 

  delayMicroseconds(60);
  fire();
  delayMicroseconds(120);
}

void Xaar128::loadBuffer64(byte *val){

  //SPI.transfer is a destructive operation. Make a copy of the array.
   byte B[64];
   memcpy(B,val,64);

   for (int i =0;i<8;i++){
    SPI.transfer(B[i]);
   }

  
}

void Xaar128::loadData(int currentRow,int singlepass){

  // int pos = (pending %(COLS/2) ) * 2;

  byte c1[8],c2[8];

  for (int i =0;i<8;i++){
    int j = int( i + (singlepass*16) );
    int k = int( j+8);
    c1[i] = pgm_read_byte(&IMAGE[currentRow][j]);
    c2[i] = pgm_read_byte(&IMAGE[currentRow][k]);
  }

  //SCK is used to clock data into the shift register on the rising edge.
  //The nSS(x) signal should be pulled LOW to enable the target chip to load new print
  //data

  //Data may be loaded into the shift register when the READY Signal has switched 
  // the inactive state. 
  // During this time, the printhead could be printing the first line of data.
  // CHECK READY SIGNAL ; ADD IT TO THE CODE.
  digitalWrite(nSS2,LOW);
  digitalWrite(nSS1,HIGH);
  this->loadBuffer64(c2);

  digitalWrite(nSS2,HIGH);
  digitalWrite(nSS1,LOW);
  this->loadBuffer64(c1);

  digitalWrite(nSS1,HIGH);   //BOTH nSS(x) disabled( HIGH) before leaving FCN.
}


bool Xaar128::fire(){
    
  // WAIT for start of READY active cycle  (READY IS ACTIVE HIGH)
  // nFIRE is active LOW & can be activated independent of data is loaded or not.

  //As the printhead starts firing the 'C-cycle' of the loaded data, 
  //the READY signal switches to the inactive state.
  
  //while(digitalRead(READY) == LOW)
  //{
   // }
    digitalWrite(nFIRE,LOW);
    // nFIRE active pulse width Max time : 120 micros
    //CHECK STATE, If Ready does not go low, it failed to fire.

    delayMicroseconds(5); // check Table of timing; Ready Max T3 = 3.35 micros
    //bool okay = (digitalRead(READY) == LOW);

    //TOTAL PRINT CYCLE TME IS 180 MICROS
   // delayMicroseconds(100);
    digitalWrite(nFIRE,HIGH);
   // delayMicroseconds(1);
    //delayMicroseconds(100);
    bool okay = true;
    return okay;
  
}


void Xaar128::PRINT(int currentSingle_Pass, int current_Row, int slanted)         //current pass , row and if print head is slanted or not > it affect how much delay in this function
{
  loadData(current_Row,currentSingle_Pass);
  delayMicroseconds(5);
  fire();
  if(slanted ==0)
  {
    delayMicroseconds(120);
  }
//  else 
//  {
//    if(slanted ==1)
//    {
//      
//    }
//  }
}
