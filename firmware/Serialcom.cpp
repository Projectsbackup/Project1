/* THIS CLASS CONSISTS OF ALL FCNS NEEDED FOR ESTABLISHING SERIAL COMMUNICATION BETWEEN 
 *  FIRMWARE AND HOST PC PROGRAM
 */

#include "Arduino.h"


class Serialcom {

//const byte numChars = 64;



public:

char tempChars[64];     // For parsing incoming Data
int currentCommand =0;

char COMMAND[10];        //COMMANDS FROM HOST , COMMANDS DOESNOT EXCEED 10 CHARS
int integerFromPC = 0;

char receivedChars[64];
boolean newData = false;
int  MMove[2]= {0,0};

Serialcom()
{
  Serial.begin(115200);
}

void start()
{
  Serial.println("Xaar Printing System 1.0");
}

void echoCommand(int cmd)
{
   String nameCommand = "";
  if(cmd == 1 ){
      nameCommand = "HOME";
    }
     if(cmd == 2){
     
      nameCommand = "START";
    }
     if(cmd == 3 ){
      
      nameCommand = "PAUSE";
    }
     if(cmd == 4){
      
      nameCommand = "CANCEL";
    }
     if(cmd == 5 ){
     
      nameCommand = "MMOV";
    }

    if(cmd == 7 ){
     
      nameCommand = "TEST";
    }
    
  Serial.println("<" + nameCommand + ">");
  
}


bool checkConnection()
{
  
    if(!Serial)
    {
      return false;
    }
    else
    {
      return true;
    }
    
}

void recvWithStartEndMarkers() 
{
      static boolean recvInProgress = false;
      static byte ndx = 0;
      char startMarker = '<';
      char endMarker = '>';
      char rc;
     
      while (Serial.available() > 0 && newData == false) 
      {
          rc = Serial.read();
         // Serial.println("rc :" + String(rc) );
          if (recvInProgress == true) 
          {
              if (rc != endMarker) 
              {
                  receivedChars[ndx] = rc;
                  ndx++;
                  
              }
              else 
              {
                  receivedChars[ndx] = '\0'; // terminate the string
                  recvInProgress = false;
                  ndx = 0;
                  newData = true;
                  strcpy(tempChars, receivedChars);
                 
                  parseData();
                  memset(receivedChars, 0, sizeof receivedChars);  // this temporary copy is necessary to protect the original data
                                                                   //   because strtok() used in parseData() replaces the commas with \0
              }
          }
  
          else if (rc == startMarker) 
          {
              recvInProgress = true;
          }
      }
}


bool checkdata()
{
  
    recvWithStartEndMarkers();
    if(newData)
    {
         newData = false;
         return true;
    }
    else
    {
        return false;
    }
   
}

void setCommand(int Com)
{
  currentCommand = Com;
  //Serial.println("comm :" + String(currentCommand));
}

int getCommand()
{
  return currentCommand;
}

int * getMMove()
{
  return MMove;
}
void set_MMove(int Mx,int My)
{
  if(Mx >-2 && Mx <2 && My >-2 && My <2)
  {
     MMove[0] = Mx;
     MMove[1] = My;
  }
}



void parseData() 
{  // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index
    int dataCount;
    
    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    if(strtokIndx == NULL)
    {
    strcpy(COMMAND, tempChars); 
    int command = checkCommand(COMMAND);
    echoCommand(command);
    }
    else 
    {
      strcpy(COMMAND,strtokIndx);
    }

    int command = checkCommand(COMMAND);
    setCommand(command);
    echoCommand(command);
    // CASE OF MANUAL MOVE , 0 STOP , 1 POS , -1 NEGATIVE
    if(command == 5)
    {
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    int movx = atoi(strtokIndx);  
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    int movy = atoi(strtokIndx);    // copy it to COMMAND STRING
    set_MMove(movx,movy);
    Serial.println("<MMOV," + String(movx)+"," +String(movy) + ">");
    }

  

}


int checkCommand(char* COMMND){
    if(strcmp(COMMND,"HOME")==0){
      return 1;
    }
     if(strcmp(COMMND,"START")==0){
      return 2;
    }
     if(strcmp(COMMND,"PAUSE")==0){
      return 3;
    }
     if(strcmp(COMMND,"CANCEL")==0){
      return 4;
    }
     if(strcmp(COMMND,"MMOV")==0){
      return 5;
    }
     if(strcmp(COMMND,"TEST")==0){
      return 7;
    }
    return -1;
}


  

};
