# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:16:05 2019

Testing serial connection between arduino Mirco- controller & sending data from Python interface



@author: Jimmy
"""

#import serial
import warnings
import serial
import serial.tools.list_ports
import time
import numpy as np
from matplotlib import pyplot as plt
from Image_Converter import Image_Converter

arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description
]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')


image_converter = Image_Converter()   
image_converter.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\spheresmaller5x.svg') 
image_to_send = image_converter.getlayer(10)
plt.imshow(image_to_send, cmap=plt.cm.gray) #interpolation='nearest'
plt.show()
## Serial.readBytes(buffer, length) in arduino 
ser = serial.Serial(arduino_ports[0], 115200,timeout=1)
#print(ser.get_settings())
time.sleep(1)   # NEEDED FOR FIRST TIME AND IN MIDDLE FOR IN_WAITING FUNCTION TO WORK
print(ser.inWaiting())
count =0
bed_image = np.zeros((96*64))
connected = False
layer_data = False

msg_sent = False
msg_sent_received = False

'''
PROGRAM CAN LOAD IMAGE DATA UP 90 X 90 MM WITHOUT SLANTING
TOTAL BYTES LOADED TO FLASH MEMORY = 192.32 KB > H 1280/8 x 1202 W
HEIGHT EQUAVILANCY = 1280 PXS > 360 RESOLUTION 90MM TO 1280
WIDTH //           = 1202 PXS > 339 RESOLUTION  90 TO 1202

'''
def write_layerdata(image_to_send):
    file = open("firmware\\image.h","w")
    file.write("#ifndef IMAGE_H_\r\n")
    file.write("#define IMAGE_H_\r\n")
    
    file.write("#define imageserial %s\r\n" %("ta3ala"))
               
    #HEIGHT > COLS TO STACK BYTES TOGETHER , WIDTH >ROWS , IMAGE IS 90 ROTATED/SHIFTED 
    COLS = int(int(image_to_send.shape[0])/8)
    ROWS = int(image_to_send.shape[1])
    file.write("#define COLS %d\r\n" % COLS)
    file.write("#define ROWS %d\r\n" % ROWS)
    
    file.write("static const byte IMAGE[ROWS][COLS] PROGMEM = {\r\n")
    image_to_send =image_to_send.astype(int)
    for i in range(0,ROWS):
        file.write("{")
        for j in range(0,COLS):
            #print((image_to_send).shape)
            
            together = (image_to_send[(j*8):(j*8)+8,i])
            together = (''.join(map(str, together)))
            if(j ==COLS-1):
                file.write("0b%s"%together)
            else:
                file.write("0b%s,"%together)
        if(i == ROWS-1):
            file.write("}\r")
        else:
            file.write("},\r")
    file.write("};\r\n")
    file.write("#endif")
    file.close()
    
def ser_write():
        #write_string = "<HOME>"
        write_string = "<CANCEL>"
        ser.write(write_string.encode('utf-8'))
        #msg_sent = True
        print("msg_sent")
       # time.sleep(0.005)

def ser_msgcheck(write_string):
        if ser.in_waiting >2:
            
            read_byte =ser.readline(ser.in_waiting) # .decode('utf-8')
           # print("read byte :")  # + read_string)
            print(read_byte)
            
            try:
                read_string = read_byte.decode('utf-8')
                
                beginning = read_string.find("<")
                end = read_string.find(">")
                if(beginning != -1 and end !=-1):
                    msg = read_string[beginning:end+1]
                    #print("msg :" + msg)
                    msgdone = True
#                elif(beginning != -1 and end == -1):
#                    msg = read_string[beginning:]
#                    msgdone = False
#                elif(beginning == -1 and end !=-1):
#                    msg += read_string[:end+1]
#                    msgdone = True
                if(msgdone == True):
                    print("msg :" + msg)
                    if(msg[:len(msg)] == write_string[:len(write_string)]):
                       # msg_sent_received = True
                        print("here")
                        return True
                    else:
                        return False
                    msg = ""
                    msgdone = False
                else:
                    return False
            except:
                    return False
        else:
            return False
                
        
def ser_read():
        if ser.in_waiting >2:
            
            read_byte =ser.readline(ser.in_waiting) # .decode('utf-8')
           # print("read byte :")  # + read_string)
          #  print(read_byte)
            try:
                read_string = read_byte.decode('utf-8')
                
                beginning = read_string.find("<")
                end = read_string.find(">")
                if(beginning != -1 and end !=-1):
                    msg = read_string[beginning:end+1]
                    msgdone = True
#                elif(beginning != -1 and end == -1):
#                    msg = read_string[beginning:]
#                    msgdone = False
#                elif(beginning == -1 and end !=-1):
#                    msg += read_string[:end+1]
#                    msgdone = True
                if(msgdone == True):
                    print("msg :" + msg)
                    msg = ""
                    msgdone = False
                
               # print("decoded :" +read_byte.decode('utf-8'))
            except:
                pass
        #time.sleep(1/10)

def send_msg(write_string):
    global msg_sent
    global msg_sent_received
    global count
    if msg_sent == False:
             ser_write()
             msg_sent = True
             
    if msg_sent_received == False and msg_sent == True and count <5:
             print("recieving")
             msg_sent_received = ser_msgcheck(write_string)
             print(msg_sent_received,msg_sent,count)
             time.sleep(0.0001)
             count = count +1
             if count >=4:
                 msg_sent = False
                 count =0

write_layerdata(image_to_send)
#ser_write()    we must make sure that msg is sent
while (ser.is_open):     #ser.in_waiting >0 or ser.out_waiting >0: #ser.in_waiting >0 & ser.:
         write_string = "<LDRC, 400, 500>"
         
         send_msg(write_string)
         if msg_sent_received == True:
             break
             #break
          
          #ser_write()
         # ser_write()
#        response = ser.readline() #.decode()
#          #time.sleep(1./120)
#          #response = ser.read()
#          print(response)
#          if(connected == False):    
#              ser.write(b"connect")
#            #  time.sleep(0.03)    # it was time.sleep(3)
#              if (response ==  b'xconnect\r\n'):
#                  connected = True
#        # HERE IS COMMAND TO PRINT IS CLICKED 
#          if(connected & layer_data ==False):
#              ser.write(b"layer_data\r\n")
#             # time.sleep(1./120)
#              
#              
#          if (response ==  b'RX:layer_data\r\n'):
#              layer_data = True
#              (rows,cols) = image_to_send.shape
#             # print( (rows).to_bytes(2, byteorder='big'))
#              ser.write(b'rows:'+(rows).to_bytes(2, byteorder='big'))
#              time.sleep(1./120)
              
             
                
              # print(int.from_bytes(b'\x01\x19', 'big'))  // from byte to int
             
             
          #response = ser.read().decode('ascii')
#          response = int(response)
#          response = format(response, "08b")
#          response = int(response)
#          
#          #print(type(response))
#          time.sleep(0.02)
#          count = count+7
#          bed_image[count-7:count+7]=response
#          #print(count)
##          print("read data: " + str(response, encoding))
#bed_image = bed_image.reshape((48,128))
#plt.imshow(bed_image, cmap=plt.cm.gray)
#print(bed_image.shape)
#print(count)
        
ser.close()
print("Serial closed")