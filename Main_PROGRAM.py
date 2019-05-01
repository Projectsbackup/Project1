# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import sys
from PyQt5.QtGui import QPixmap, QColor, QImage
# from Image_Converter import Image_Converter
# from visualization import visualization as vis
# from Ui_MainWindow import Ui_MainWindow
#from subfolder.visualization import visualization as vis


from subfolder.Ui_MainWindow import Ui_MainWindow
from subfolder.Serial_test import Serial_test as Serial
from subfolder.Image_Converter import Image_Converter

import matplotlib
from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
import subprocess

import matplotlib.animation as manimation
#import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as M3
import mpl_toolkits.mplot3d.art3d as art3d


#from Serial_test import Serial_test as Serial
import serial.tools.list_ports
import threading
from functools import partial
import time
import os
#import OpenGL.GL as gl
#import OpenGL.GLU as glu
#import OpenGL.GLUT as glut
#import os

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches

# image_converter = Image_Converter()   
# image_converter.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\spheresmaller5x.svg') 
# image_to_send = image_converter.getlayer(10)

class Main_PROGRAM(QtWidgets.QMainWindow):
    
    def __init__(self):
         super().__init__() 
         self.ui = Ui_MainWindow()
         self.MainWindow = QtWidgets.QMainWindow()
         self.ui.setupUi(self.MainWindow)
        
        
         #self.uiSTL = Ui_StlSlicer()
         #self.StlWindow = QtWidgets.QMainWindow()
         #self.uiSTl.stepui(self.StlWindow)
        
         self.image_converter = Image_Converter()
         
         
         self.display_layer_counter =0
         self.model_layers = []
          
         self.serial = Serial()
         self.connection = 0
         
         # " for manual commands
         self.statx =0
         self.staty =0
         
         self.done_data = False
         
         self.fileName = ""
         
         self.link_ui()
         self.MainWindow.show()
         
         #self.link_uistl()
        
         self.slantdata = False
         
         self.timer = QtCore.QTimer(parent=self)
         self.timer.setInterval(1)
         self.timer.timeout.connect(self.check_connection)
         self.timer.start()
         self.tt =0
         
         
    def link_uiStl(self):
        self.uiStl.centerIt.clicked.connect(self.stlcenter())
        self.uiStl.auto_scale.clicked.connect(partial(self.stlscale(),1))
        self.uiSTL.ScaleSTL.clicked.connect(partial(self.stlscale(),0))
        self.uiSTL.TranslateSTL.clicked.connect(self.stlTranslate())
        self.uiSTL.RotateSTL.clicked.connect(self.stlRotate())
        self.uiSTL.SliceSTl.clicked.connect(self.stlSlice())
        self.uiSTL.OPenSlic3r.clicked.connect(self.stlOpenSlic3r())
        
        bedsizeX = self.ui.bedXaxis.value()
        bedsizeY = self.ui.bedYaxis.value()
        self._canvas3,self.ax3 = self.create_fig("3d",bedsizeX,bedsizeY)
        self._canvas3.setParent(self.uiSTL.viewstl)
        self._canvas3.draw()
        
    
    
    
    def link_ui(self):
       
       
        self.ui.slicer.clicked.connect(self.openSlic3r)
        
        self.ui.print.clicked.connect(partial(self.send_commands,"print"))
        
        self.ui.cancelprint.clicked.connect(partial(self.send_commands,"cancel"))
        
        self.ui.pauseprint.clicked.connect(partial(self.send_commands,"pause"))
        
        self.ui.homebutton.clicked.connect(partial(self.send_commands,"home"))
        self.ui.testprinthead.clicked.connect(partial(self.send_commands,"test_printhead"))
        self.ui.movenegx.clicked.connect(partial(self.set_statusX,-1))
        self.ui.stopx.clicked.connect(partial(self.set_statusX,0))
        self.ui.moveposx.clicked.connect(partial(self.set_statusX,1))
        self.ui.movenegy.clicked.connect(partial(self.set_statusY,-1))
        self.ui.stopy.clicked.connect(partial(self.set_statusY,0))
        self.ui.moveposy.clicked.connect(partial(self.set_statusY,1))
        
        self.ui.opensvg.clicked.connect(self.openFileNameDialog)
        #self.ui.layernumb.valueChanged.connect(self.layervalue)
        self.ui.uploaddata.clicked.connect(self.upload_data)
        
        
        
        self.ui.manualOFF.clicked.connect(partial(self.send_commands,"OFF"))
        
        
        
        
        
        bedsizeX = self.ui.bedXaxis.value()
        bedsizeY = self.ui.bedYaxis.value()
        self._canvas2,self.ax2 = self.create_fig("3d",bedsizeX,bedsizeY)
        self._canvas2.setParent(self.ui.view3d)
        self._canvas2.draw()
        self._canvas1,self.ax1 = self.create_fig("2d",bedsizeX,bedsizeY)
        self._canvas1.setParent(self.ui.LAYER_VIEW2D)
        self._canvas1.draw()
        
        self.update_parameters(0)
        self.ui.updateParameters.clicked.connect(partial(self.update_parameters,1))
       
    
             #change gui singlepassdimen to double qspin and check for slant option  
               # to do clean code , write a write parameter function , test for multiple model loading , off button encoding , set figures and draw3d 2d right
    def update_parameters(self,clicked):   #clicked to update =1 , first time clicked =0
        if clicked == 1:
            self.ui.updateParameters.setEnabled(False)
            QtWidgets.QApplication.processEvents()
            
        self.dpiX = self.ui.Xdpi.value()
        self.dpiY = self.ui.Ydpi.value()
        
        self.image_converter.setdpiX(self.dpiX)
        self.image_converter.setdpiY(self.dpiY)
        
        self.CalibX = self.ui.bedXorigin.value()
        self.CalibY = self.ui.bedYorigin.value()
        
        self.BedsizeX = self.ui.bedXaxis.value()
        self.BedsizeY = self.ui.bedYaxis.value()
        self.BedsizeZ = self.ui.bedZaxis.value()
        
        self.stepPerPixel = self.ui.Pstep_pixel.value()
        self.StepPixelDuration = self.ui.Pduration_step.value()
        self.singlePassDim = self.ui.singlepassDimension.value()
        
        self.jetFreq = self.ui.jet_freq.value()
        
        self.motorXResln = self.ui.xmotionresln.value()
        self.motorYResln = self.ui.ymotionresln.value()
        self.motorXspd = self.ui.xmotionspd.value()
        self.motorYspd = self.ui.ymotionspd.value()
        
        if(self.stepPerPixel ==1):
            XMtrSpd = (self.motorXResln *1000)/40   #max speed can be achieved in this setup [stepper motors]
        else:
            if((self.StepPixelDuration/2)>= 40):
                XMtrSpd = (self.motorXResln * 1000) /self.StepPixelDuration
            if((self.StepPixelDuration/2) <40):
                XMtrSpd = (self.motorXResln *1000)/40
                self.ui.textBrowser.append("*Please change Step/Duration Setting: Min duration for 1 step is : 40 Microseconds")
        YMtrSpd = (self.motorYResln *1000)/40 
        if(self.motorXspd ==0 or self.motorXspd > XMtrSpd):
            self.ui.textBrowser.append("*X Motor speed readjusted to fit Max possible speed: %s" % XMtrSpd)
        
        if(self.motorYspd ==0 or self.motorYspd > YMtrSpd):
            self.ui.textBrowser.append("*Y Motor speed readjusted to fit Max possible speed: %s" % YMtrSpd)
       
        if(self.ui.slantData.isChecked()):
            self.slantdata = True
            
        else:
            self.slantdata = False
        if(self.ui.Xreversed.isChecked()):
            self.XPrintDirection = "XHOMEDIR"
            self.XPrint_return = "XAWAYDIR"
        else:
            self.XPrintDirection = "XAWAYDIR"
            self.XPrint_return = "XHOMEDIR"
        if(self.ui.Yreversed.isChecked()):
            self.YPrintDirection = "YHOMEDIR"
            self.YPrint_return = "YAWAYDIR"
        else:
            self.YPrintDirection = "YAWAYDIR"
            self.YPrint_return = "YHOMEDIR"
            
        if(self.ui.slantData.isChecked()):
            self.slant = True
        self.writeParameters()
        if(self.fileName):
            self.image_converter.openfile(self.fileName)  #time.ctime() +
            self.ui.textBrowser.append('<span style="color:darkolivegreen">* Parameters and Model updated, please upload.</span>')
            self.update_2d()
            layer_numbers = self.image_converter.get_model_layers_numb()
            self.ax2 = self.draw3d(self.ax2,layer_numbers)
            self._canvas2.draw()
            if clicked == 1:
                self.ui.updateParameters.setEnabled(True)
        else:
            
            self.ax2 = self.axes_update(self.ax2)
            self._canvas2.draw()
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Parameters updated, Please upload.</span>')
            if clicked == 1:
                
                self.ui.updateParameters.setEnabled(True)
    
    
    def writeParameters(self):
        file = open("firmware\\printparameters.h","w")
        file.write("#ifndef PRINTPARAMETERS_H_\r\n")
        file.write("#define PRINTPARAMETERS_H_\r\n")
        
        file.write("#define dpiX %d\r\n" % self.dpiX)
        file.write("#define dpiY %d\r\n" % self.dpiY)
                   
        file.write("#define CalibX %d\r\n" % self.CalibX)
        file.write("#define CalibY %d\r\n" % self.CalibY)
        
        file.write("#define BedsizeX %d\r\n" % self.BedsizeX)
        file.write("#define BedsizeY %d\r\n" % self.BedsizeY)
        file.write("#define BedsizeZ %d\r\n" % self.BedsizeZ)
                   
        file.write("#define StepPrintPixel %d\r\n" % self.stepPerPixel)
        file.write("#define StepPrintduration %d\r\n" % self.StepPixelDuration)
        
        file.write("#define singlepassDim %d\r\n" % self.singlePassDim)
        file.write("#define jetFreq %d\r\n" % self.jetFreq)
        
        file.write("#define motorXResln %d\r\n" % self.motorXResln)
        file.write("#define motorYResln %d\r\n" % self.motorYResln)
        
        file.write("#define motorXspd %d\r\n" % self.motorXspd)
        file.write("#define motorYspd %d\r\n" % self.motorYspd)
        
        file.write("#define XPrintDirection %s\r\n" % self.XPrintDirection)
        file.write("#define YPrintDirection %s\r\n" % self.YPrintDirection)
        
        file.write("#define XPrint_return %s\r\n" % self.XPrint_return)
        file.write("#define YPrint_return %s\r\n" % self.YPrint_return)
                   
        file.write("#endif")
        file.close()
    def axes_update(self,ax):
         xlim = self.BedsizeX +20
         ylim = self.BedsizeY +20
         zlim = self.BedsizeZ +20
         ax.set_xlim([0, xlim]) #2125
         ax.set_ylim([0, ylim]) #2125
         ax.set_zlim([0,zlim ])
         major_ticksx = np.arange(0, xlim, 20)
         minor_ticksx = np.arange(0, xlim, 5)
         
         major_ticksy = np.arange(0, ylim, 20)
         minor_ticksy = np.arange(0, ylim, 5)
            
         major_ticksz = np.arange(0, zlim, 20)
         minor_ticksz = np.arange(0, zlim, 5)

         ax.set_xticks(major_ticksx)
         ax.set_xticks(minor_ticksx, minor=True)
         ax.set_yticks(major_ticksy)
         ax.set_yticks(minor_ticksy, minor=True)
            
         ax.set_zticks(major_ticksz)
         ax.set_zticks(minor_ticksz, minor=True)

      # And a corresponding grid
         ax.grid(which='both')

       # Or if you want different settings for the grids
         ax.grid(which='minor', alpha=0.2)
         ax.grid(which='major', alpha=0.5)
         return ax
    
    
    def Export_Model_Printing_data(self):
        if(self.image_converter.get_model_layers_numb() <1):
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">please upload a Model first</span>')
        else:
            loc =r"\Layer_data"
            if len(os.listdir(os.getcwd()+loc) ) == 0:
                start = time.time()
                ia =self.image_converter.poly2imgWrite(self.image_converter.getlayer_data(0),self.image_converter.get_totalLayer_shape(0))
                np.savetxt(loc+"\Layer"+str(0) +".txt",ia, fmt = '%d',delimiter=',',newline ='\n',header ='[',footer =']')
                end1 = time.time()
                self.ui.textBrowser.append("*Generating Model data of %d layers, Estimated Time: %d seconds" % (self.image_converter.get_model_layers_numb(),(end1-start)*self.image_converter.get_model_layers_numb()) ) 
                for i in range(1,self.image_converter.get_model_layers_numb()):
                    ia =self.image_converter.poly2imgWrite(self.image_converter.getlayer_data(i),self.image_converter.get_totalLayer_shape(i))
                    np.savetxt(loc+"\Layer"+str(i) +".txt",ia, fmt = '%d',delimiter=',',newline ='\n',header ='[',footer =']')
            else:
                self.ui.textBrowser.append("*please Empty the 'Layer_data' folder in the program directory")
    
    def layervalue(self,lv):
        self.ui.layernum.setText("layer " +str(lv) + "/" + str(self.image_converter.get_model_layers_numb()))
        if self.ui.tab2dview.currentIndex() !=self.ui.tab2dview.indexOf(self.ui.view2d) :
            self.ui.tab2dview.setCurrentIndex(self.ui.tab2dview.indexOf(self.ui.view2d))
            
    def set_statusX(self,statx):
        self.statx = statx
        self.send_commands("MMOV")
    def set_statusY(self,staty):
        self.staty = staty
        self.send_commands("MMOV")
        
    def send_commands(self,name):
        if self.serial.check_connectn():
            if name == "print":
                
                self.serial.ser_write("START")
                
                
            if name == "cancel":
                self.serial.ser_write("CANCEL")
            if name == "home":
                self.serial.ser_write("HOME")
            if name == "pause":
                self.serial.ser_write("PAUSE")
            if name == "MMOV":
                
                to_send = "MMOV," + str(self.statx) +","+ str(self.staty)
                self.serial.ser_write(to_send)
            
            if name == "OFF":
                
                to_send = "MMOV,0,0" 
                self.serial.ser_write(to_send)
                
            if name =="test_printhead":
                self.serial.ser_write("TEST")
        else:
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Printer is not connected</span>')
        
        
    def checkmsg(self,msg):
        print("msg her:" + msg)
        if msg == "<HOME>":
            self.ui.process.setText("Homing")
        elif msg == "<START>":
            self.ui.process.setText("Printing Started")
            self.ui.print.setEnabled(False)
        elif msg == "<PAUSE>":
            self.ui.process.setText("Process Paused")
            self.ui.print.setText("PRINT/CONTINUE")
            self.ui.print.setEnabled(True)
        elif msg == "<CANCEL>":
            self.ui.process.setText("Process Cancelled")
            self.ui.print.setText("PRINT")
            self.ui.print.setEnabled(True)
        elif msg == "<MMOV>":
            self.ui.process.setText("Manual Motion Control")
        elif msg == "<TEST>":
            self.ui.process.setText("Printhead Test")
        else:
            self.ui.textBrowser.append(msg)
            
    def close_connection(self):
        self.serial.disconnect()
        
        
    def check_connection(self):
            #print("check")
          
            if self.serial.connect()== True and self.connection !=1:
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Printer is connected</span>')
                self.ui.connectionstatus.setText("Connected")
                self.connection = 1
                
                #return True
#            
            else:
                if self.serial.connect() == False and self.connection != 2:
                    self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Printer is disconnected</span>')
                    self.ui.connectionstatus.setText("Disconnected")
                    self.connection = 2
                    
                #return False
                if self.serial.connect() ==3 and self.connection !=3:
                    self.connection =3
                    self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">"Connection could not be established, please reconnect device and restart program"</span>')
            if self.serial.check_connectn() == True: 
                msg = self.serial.ser_read()
                
                if(msg):
                    self.checkmsg(msg)
    
    def arduino_upload(self):
        
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description
                ]
        arduinoProg = "\"C:\\Program Files (x86)\\Arduino\\arduino\""
    
        actionLine = "upload "
    
        boardLine = "arduino:avr:mega"
        portLine = arduino_ports[0]
        projectFile2 = "\"\\firmware\\firmware.ino\""
        arduinoCommand = arduinoProg  + " --board " + boardLine + " --port " + portLine + " --" + actionLine + projectFile2
        print("\n\n -- Arduino Command --")
        print(arduinoCommand)
    
        print("-- Starting %s --\n")
    
        presult = subprocess.call(arduinoCommand, shell=True)
    
        if presult != 0:
            #print("\n Failed - result code = %s --" %(presult))
            return False
        else:
                #print("\n-- Success --")
                return True
    def done_upload(self):
        self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Done uploading</span>')
        
        self.connection =0
        #self.timer = QtCore.QTimer(parent=self)
        self.timer.timeout.disconnect(self.done_upload)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.check_connection)
        self.timer.start()
        self.done_data = True
        self.ui.print.setEnabled(True)
#        if self.tt.isAlive():
#            print("ALIVE")
#            self.tt.join()
    def upload_data(self):
        if( self.serial.check_connectn()== True and self.image_converter.get_model_layers_numb() >0): #self.serial.connect()== True and
            image_numb = self.ui.layernumb.value()
            self.ui.layernumb.setEnabled(False)
            
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Uploading data...please wait</span>')
            #image_to_send = self.image_converter.getlayer(image_numb)
            image_to_send = self.image_converter.getlayer_data(image_numb)
            image_to_send = self.image_converter.poly2imgWrite(image_to_send,self.image_converter.get_totalLayer_shape(image_numb))
            if(self.slantdata == True):
                image_to_send = self.slant_image(image_to_send,128)
                
            self.serial.write_layerdata(image_to_send)
            print("done writing")
            self.timer.stop()
            self.serial.disconnect()
            if(self.arduino_upload() == True):
                 
                 self.timer.setInterval(30000)
                 self.timer.timeout.connect(self.done_upload)
                 self.timer.start()
#                self.tt = threading.Timer(30,self.done_upload)
#                self.tt.daemon = True
#                self.tt.start()
            else:
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Upload failed</span>')
        else:
            if(self.serial.check_connectn()== False):
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Printer is not connected</span>')
            if(not self.image_converter.get_model_layers_numb() ):
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">No Data</span>')
            #self.done_upload()
    
    def slant_image(self,imgg,nozzles=128):
         ite = self.image_converter.img_getheight()
         ite = ite/nozzles
         nozz = nozzles -2  # repeat the process for the inbetween 126 nozzles
         for i in range(0,int(ite)):
             for j in range(0,nozz,3):  #last item in range not counted
                 k = j + (i*128)
                 if(j ==0):
                     
                     imgg[k+1,:] = np.roll(imgg[k,:],2)
                     imgg[k+2,:] = np.roll(imgg[k,:],3)
                     imgg[k+3,:] = np.roll(imgg[k,:],5)
                 else:
                    
                        
                     imgg[k+1,:] = np.roll(imgg[k+1,:],2+int(5*j/3))
                     imgg[k+2,:] = np.roll(imgg[k+2,:],3+int(5*j/3))
                     imgg[k+3,:] = np.roll(imgg[k+3,:],5+int(5*j/3))
                        
             imgg[127+(i*128),:]  = np.roll(imgg[127+(i*128),:],2+int(5*42))
                        
         return imgg
    def image_draw(self):
       
        self.ax.imshow(image_to_send[0:self.count,0:self.count],origin='upper', aspect='auto')
        self._canvas.draw()
        self.count = self.count +5
        
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        
        self.fileName, _ = QFileDialog.getOpenFileName(self,"Select Silc3r SVG File", r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES',"SVG Files (*.svg);;All Files (*)", options=options)
        if self.fileName:
           # self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">File being processed</span>')
            #print(fileName)
            self.done_data = False
            self.ui.print.setEnabled(False)
            modelname = self.fileName.split("/")[-1]
            modelname = modelname.split(".")[0]
            self.ui.modelname.setText(modelname)
            #return fileName
            self.model_layers =[]
            file_status = self.image_converter.openfile(self.fileName)
            if(file_status):
                #self.model_layers = self.image_converter.get_model_layers()
                layer_numbers = self.image_converter.get_model_layers_numb()
              
                self.ui.layernumb.setEnabled(True)
              
                self.ui.layernumb.setMaximum(layer_numbers)
                
                self.ax1.clear()
                self.ax2 = self.draw3d(self.ax2,layer_numbers)
                self.ax1 = self.draw2d(self.ax1,0)
                
    #            imggg = self.image_converter.getlayer(0)
    #            imggg =self.slant_image(imggg,128)
    #            
    #            plt.imshow(imggg, cmap=plt.cm.gray) #interpolation='nearest'
    #            plt.show()
                
                self._canvas1.draw()
                self._canvas2.draw()
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Model Found & processed</span>')
                self.ui.layernum.setText("layer " +str(self.ui.layernumb.value()) + "/" + str(self.image_converter.get_model_layers_numb()))
                self.ui.layernumb.valueChanged.connect(self.update_2d)
                
            else:
                self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">File is invalid or does not exist</span>')
           
            
  
    def openSlic3r(self):
        #self.MainWindow.setEnabled(False)
        #subprocess.call(['C:\Program Files\Repetier-Host\Slic3r\Slic3r.exe'])
        process =subprocess.Popen('C:\Program Files\Repetier-Host\Slic3r\Slic3r.exe', shell=False)
        
        #self.MainWindow.setEnabled(True)
#    def tabSelected(self, arg=0):
#        print(arg)
#        if(arg ==0):
#            self.draw()
   
   
    def update_2d(self):
        layer_value = self.ui.layernumb.value()
        #print(layer_value)
        self.layervalue(layer_value)
        
        self.ax1 = self.draw2d(self.ax1,layer_value)
        self.ax1.plot()
        #self._canvas1.figure.tight_layout()
        self._canvas1.draw()
        self._canvas1.flush_events()
       
        
        #self._canvas1.draw()
        #self.ui.layernumb.setValue(layer_value)
        
        
        
    
           
    def create_fig(self,proj,xlim,ylim):
        #sns.set()
        plt.style.use('seaborn')
        _canvas = FigureCanvas(Figure(figsize=(8.7,5.3),dpi =100))
        
        if(proj == "2d"):
             ax = _canvas.figure.add_subplot(111)
             
             ax.set_xlim([0, xlim]) #2125
             ax.set_ylim([0, ylim]) #2125
      #  self.ax.set_zlim([0,30])
             major_ticks = np.arange(0, xlim, 100)
             minor_ticks = np.arange(0, ylim, 5)

             ax.set_xticks(major_ticks)
             ax.set_xticks(minor_ticks, minor=True)
             ax.set_yticks(major_ticks)
             ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
             ax.grid(which='both')

        # Or if you want different settings for the grids:
             ax.grid(which='minor', alpha= 0.2)
             ax.grid(which='major', alpha=0.5)
             _canvas.figure.tight_layout()
             _canvas.move(-15,-30)
             return _canvas,ax
         
        if(proj == "3d"):
             ax = _canvas.figure.add_subplot(111,projection ='3d')
            # ylim = int(self.BedsizeY) #*(self.dpiY/25.4))
            # xlim = int(self.BedsizeX) #*(self.dpiX/25.4))
             zlim = self.ui.bedZaxis.value() +20
             xlim = xlim+20
             ylim = ylim+20
             ax.set_xlim([0, xlim]) #2125
             ax.set_ylim([0, ylim]) #2125
             ax.set_zlim([0,zlim ])
             major_ticksx = np.arange(0, xlim, 20)
             minor_ticksx = np.arange(0, xlim, 5)
            
             major_ticksy = np.arange(0, ylim, 20)
             minor_ticksy = np.arange(0, ylim, 5)
            
             major_ticksz = np.arange(0, zlim, 20)
             minor_ticksz = np.arange(0, zlim, 5)

             ax.set_xticks(major_ticksx)
             ax.set_xticks(minor_ticksx, minor=True)
             ax.set_yticks(major_ticksy)
             ax.set_yticks(minor_ticksy, minor=True)
            
             ax.set_zticks(major_ticksz)
             ax.set_zticks(minor_ticksz, minor=True)

         # And a corresponding grid
             ax.grid(which='both')

        # Or if you want different settings for the grids:
             ax.grid(which='minor', alpha=0.2)
             ax.grid(which='major', alpha=0.5)
            
             _canvas.figure.tight_layout()
             _canvas.move(-50,-30)
             return _canvas,ax
         
    def draw3d(self,axes,layers):
            axes.clear()
            
            h,w = self.image_converter.getCadModelDim()
            shiftH = int((self.BedsizeY - h) /2)
            shiftW = int((self.BedsizeX - w) /2)
            for j in range(0,layers):
                layer_data =  self.image_converter.getlayer_data(j)
                for i in range(0,len(layer_data)):
                    temp_layer = layer_data[i].copy()
                    temp_layer[:,0] = (temp_layer[:,0]/(self.dpiX/25.4) ) +shiftH
                    temp_layer[:,1] = (temp_layer[:,1]/(self.dpiY/25.4) ) +shiftW
                    temp_layer = temp_layer.astype(int)
                    #path = Path(layer_data[i])
                    path = Path(temp_layer)
                    patch = patches.PathPatch(path)
                    axes.add_patch(patch)
                    art3d.pathpatch_2d_to_3d(patch, z=j, zdir='z')
                   
            ylim = int(self.BedsizeY)+20 #*(self.dpiY/25.4))
            xlim = int(self.BedsizeX)+20 #*(self.dpiX/25.4))
            zlim = self.BedsizeZ +20
            
            axes.set_xlim([0, xlim]) #2125
            axes.set_ylim([0, ylim]) #2125
            axes.set_zlim([0,zlim])
            major_ticksx = np.arange(0, xlim, 20)
            minor_ticksx = np.arange(0, xlim, 5)
            
            major_ticksy = np.arange(0, ylim, 20)
            minor_ticksy = np.arange(0, ylim, 5)
            
            major_ticksz = np.arange(0, zlim, 20)
            minor_ticksz = np.arange(0, zlim, 5)

            axes.set_xticks(major_ticksx)
            axes.set_xticks(minor_ticksx, minor=True)
            axes.set_yticks(major_ticksy)
            axes.set_yticks(minor_ticksy, minor=True)
            
            axes.set_zticks(major_ticksz)
            axes.set_zticks(minor_ticksz, minor=True)

        # And a corresponding grid
            axes.grid(which='both')

        # Or if you want different settings for the grids:
            axes.grid(which='minor', alpha=0.2)
            axes.grid(which='major', alpha=0.5)
            return axes
        
    def draw2d(self,axes,layer):
       # axes.clear() #clears data only
        
        layer_data =  self.image_converter.getlayer_data(layer)
        layer_shape = self.image_converter.get_totalLayer_shape(layer)
        temp_img =self.image_converter.poly2imgWrite(layer_data,layer_shape)
        axes.imshow(self.image_converter.poly2imgWrite(layer_data,layer_shape),cmap = "GnBu")
         
        ylim = self.image_converter.img_getheight()
        xlim = self.image_converter.img_getWidth() 
        axes.set_xlim([0, xlim]) #2125
        axes.set_ylim([0, ylim]) #2125
            
        major_ticksx = np.arange(0, xlim, 100)
        minor_ticksx = np.arange(0, xlim, 5)
        
        major_ticksy = np.arange(0, ylim, 100)
        minor_ticksy = np.arange(0, ylim, 5)

        axes.set_xticks(major_ticksx)
        axes.set_xticks(minor_ticksx, minor=True)
        axes.set_yticks(major_ticksy)
        axes.set_yticks(minor_ticksy, minor=True)

        # And a corresponding grid
        #axes.grid(which='both')

        # Or if you want different settings for the grids:
        #axes.grid(which='minor', alpha=0.2)
       # axes.grid(which='major', alpha=0.5)
        axes.grid(which='minor', color='b', linestyle='-', linewidth=0.5)
        axes.grid(which='major', color='b', linestyle='-', linewidth=1)
        return axes
   
#if __name__.endswith('__main__'):
    #m = Main_PROGRAM()
   # m.link_ui()
if __name__=='__main__':
        
        app = QtWidgets.QApplication(sys.argv)
        
#        file = QtCore.QFile("dark.qss")
#        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
#        stream = QtCore.QTextStream(file)
#        app.setStyleSheet(stream.readAll())
        
        
        m = Main_PROGRAM()
       
        
        app.aboutToQuit.connect(m.close_connection)
        sys.exit(app.exec_())
        #sys.exit(app.exec_())
    #app.aboutToQuit.connect(sys.exit(app.exec_()) )
   #m.MainWindow.show()
#   if app.exec_() ==0 and m.check_connection == True:
#      
#       m.close_connection()
#       print("closed")
       
    