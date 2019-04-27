# -*- coding: utf-8 -*-
import subprocess
import serial.tools.list_ports
import time

arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description
]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')
    
    
arduinoProg = "\"C:\\Program Files (x86)\\Arduino\\arduino\""

actionLine = "upload "

boardLine = "arduino:avr:mega"

#projectFile = "C:\Users\Jimmy\Desktop\3D Printing research\Software\Arduino Code\Testing\sketch_mar14a"

portLine = arduino_ports[0]
projectFile1 = "\"C:\\Program Files (x86)\\Arduino\\examples\\01.Basics\\Blink\\Blink.ino\""

projectFile2 = "\"\\firmware\\firmware.ino\""
arduinoCommand = arduinoProg  + " --board " + boardLine + " --port " + portLine + " --" + actionLine + projectFile2

print("\n\n -- Arduino Command --")
print(arduinoCommand)

print("-- Starting %s --\n")

presult = subprocess.call(arduinoCommand, shell=True)

if presult != 0:
 print("\n Failed - result code = %s --" %(presult))
else:
 print("\n-- Success --")
 #takes 10 seconds to finish process
 
