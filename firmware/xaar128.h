#ifndef XAAR128_H_
#define XAAR128_H_

#ifdef ARDUINO_AVR_MEGA2560

// Xaar Chip Select Pins for enabling Data to transfer
// TOTAL PINS TO DEFINE : 12
#define nSS1        10
#define nSS2        7

#define nCLK        11       // TIMER 1 OCR1A OUTPUT ACCORDING TO MEGA PIN-MAPPING
#define xVDD        23       // 5V FOR THE RELAY FOR THE XAAR 128 LOGIC REGISTERS

#define relayVHCH   49
#define relayVHCL   48

// SPI Communication PINS
#define SCK         52
#define MISO        50      // Master In Slave Out Pin
#define MOSI        51      // Master Out Slave In Pin

#define nRESET      8
#define nFIRE       5

#define READY       2      // This will be an Interrupt Pin 

#endif
/*.............................*/

class Xaar128 {

  public:
    int readyState = 0;   //State Condition for the Xaar 128 > It will be modified later

    Xaar128();

    // Functions to be modified to boolean for checking powerup, powerdown, .. Status of Xaar128
    void init();
    void powerUp();
    void powerDown();
    void loadBuffer64(byte *val);
    void loadData(int currentRow,int singlepass);
    bool fire();
    void PRINT(int currentSingle_Pass, int current_Row, int slanted);
    void Test();
};

#endif
