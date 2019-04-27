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
         self.MainWindow.show()
         
         #self.ui.show()
		
         self.image_converter = Image_Converter()
         
         
         self.display_layer_counter =0
         self.model_layers = []
          
         self.serial = Serial()
         self.connection = 0
         
         # " for manual commands
         self.statx =0
         self.staty =0
         
         self.done_data = False
         self.link_ui()
         
		 
         self.timer = QtCore.QTimer(parent=self)
         self.timer.setInterval(1)
         self.timer.timeout.connect(self.check_connection)
         self.timer.start()
         self.tt =0
         
         
         
    def link_ui(self):
       
        #self.ui.verticalSlider.setRange(0,len(self.model_layers)-1) #changed
       # self.ui.verticalSlider.valueChanged['int'].connect(self.disp_layers)
        #self.display_curr_layer(len(self.model_layers),self.display_layer_counter)
       # self.ui.verticalSlider.setEnabled(False)
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
        self.ui.layernumb.valueChanged.connect(self.layervalue)
        self.ui.uploaddata.clicked.connect(self.upload_data)
        
        self.ui.print.setEnabled(False)
        self.ui.pauseprint.setEnabled(True)
        self.ui.cancelprint.setEnabled(True)
        self.ui.moveposx.setEnabled(True)
        self.ui.testprinthead.setEnabled(True)
        self.ui.homebutton.setEnabled(True)
      #  sns.set()
       # fig = plt.figure(figsize=(8.82,5.55),dpi =100,frameon=False)  #8,5
#        ax = fig.add_subplot(111,projection ='3d')
#        t = np.linspace(0, 500, 501)
#        ax.set_xlim([0, 150])
#        ax.set_ylim([0, 150]) #2125
#       # ax.imshow(image_to_send) 
#       # fig.tight_layout()
#        ax.view_init(elev=90, azim=90)
#        ax.plot(t, np.tan(t), ".")
        
        
#        self.ui.LAYER_VIEW2D = FigureCanvas(fig)
#        self.ui.LAYER_VIEW2D.figure.canvas.draw()
#        self.ui.LAYER_VIEW2D.repaint()
        
        self._canvas = FigureCanvas(Figure(figsize=(8.7,5.3),dpi =100))  #resolution 3d 8.82,5.55
        
        #self.ax = self._canvas.figure.add_subplot(111,projection ='3d')
        self.ax = self._canvas.figure.add_subplot(111)
        t = np.linspace(10, 500, 501)
        
#        x, y = np.ogrid[0:image_to_send.shape[0], 0:image_to_send.shape[1]]
#        ax.plot(image_to_send[:,1],image_to_send[:,0])
#        xplot = np.where(image_to_send[:,0] == 1)[0]
#        yplot = np.where(image_to_send[:,1] == 1)[0]
#        ax.plot(xplot,yplot)
       # print(image_to_send[:,0])
#        verts = [
#                (0., 0.), # left, bottom
#                (0., 1.), # left, top
#                (1., 1.), # right, top
#                (1., 0.), # right, bottom
#                (0., 0.), # ignored
#                ]
#
#        codes = [Path.MOVETO,
#         Path.LINETO,
#         Path.LINETO,
#         Path.LINETO,
#         Path.CLOSEPOLY,
#         ]
#        
#        path = Path(image_to_send)
#        patch = patches.PathPatch(path)
#        ax.add_patch(patch)
        self.ax.set_xlim([0, 512]) #2125
        self.ax.set_ylim([0, 472]) #2125
      #  self.ax.set_zlim([0,30])
        major_ticks = np.arange(0, 513, 100)
        minor_ticks = np.arange(0, 513, 5)

        self.ax.set_xticks(major_ticks)
        self.ax.set_xticks(minor_ticks, minor=True)
        self.ax.set_yticks(major_ticks)
        self.ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
        self.ax.grid(which='both')

        # Or if you want different settings for the grids:
        self.ax.grid(which='minor', alpha=0.2)
        self.ax.grid(which='major', alpha=0.5)
        #ax.set_zlim([0, 0])
        
            
       # ax.imshow(image_to_send,origin='upper', aspect='auto') 
       
       # fig.tight_layout()
        #ax.view_init(elev=-90, azim=-90)
       # ax.plot(t, np.tan(t), ".")
        #self._canvas.setFixedSize(800, 490)
        #self.ui.LAYER_VIEW2D.setFixedSize(800, 490)
#        self._canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
#                                   QtWidgets.QSizePolicy.Expanding)
#        self._canvas.updateGeometry()
        
        #self._canvas.resize(800, 490)
        self._canvas.figure.tight_layout()
       # print(image_converter.img_getWidth())
#        self._canvas2,self.ax2 = vis.create_fig("3d",image_converter.img_getheight(),image_converter.img_getWidth())
#        self._canvas2,self.ax2 = vis.draw3d(fig,ax,image_converter.get_model_layers())
        bedsizeX = self.ui.bedXaxis.value()
        bedsizeY = self.ui.bedYaxis.value()
        self._canvas2,self.ax2 = self.create_fig("3d",bedsizeX,bedsizeY)
        self._canvas2.setParent(self.ui.view3d)
        self._canvas2.draw()
        self._canvas1,self.ax1 = self.create_fig("2d",bedsizeX,bedsizeY)
        self._canvas1.setParent(self.ui.LAYER_VIEW2D)
        self._canvas1.draw()
        self._canvas1.move(-50,-30)
#        self._canvas.setParent(self.ui.view3d)
#        self._canvas.draw()
        #self._canvas.setParent(self.ui.view3d)   # was self.ui.LAYER_VIEW2D
       # self._canvas.move(-50,-50)  #MOVES THE FIGURE 3d
        self._canvas.move(-50,-30)  # was -20,-30
#        self.ui.LAYER_VIEW2D.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
#                                   QtWidgets.QSizePolicy.Expanding)
       # self.ui.LAYER_VIEW2D.updateGeometry()
       # self._canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # layer_data =  image_converter.getlayer_data(10)
        
        
        
        # zs = np.linspace(0,2,0.1)
        # print(zs)
        # for j in range(0,19):
            # layer_data =  image_converter.getlayer_data(j)
            # for i in range(0,len(layer_data)):
                
                # path = Path(layer_data[i])
                # patch = patches.PathPatch(path)
             #   self.ax.add_patch(patch)
             #   art3d.pathpatch_2d_to_3d(patch, z=j, zdir='z')
#        coll = matplotlib.collections.PatchCollection(patchesx)
#        M3.art3d.patch_collection_2d_to_3d(coll, zs, zdir='z')
#        self.ax.add_collection(coll)
#        self.ax.show()
        #self.ax.add_patch(patch)
        self.count =5
        self.ui.manualON.clicked.connect(self.image_draw)       
       #ax.imshow(image_to_send[0:i,0:j],origin='upper', aspect='auto')
        self._canvas.draw()
               # time.sleep(1)
        
#        dynamic_ax = dynamic_canvas.figure.subplots()
#        
#        dynamic_ax.plot(t, np.tan(t), ".")
#       
#       
#        dynamic_canvas.draw()
    def update_parameters(self,clicked):   #clicked to update =1 , first time clicked =0
        #self.dpiX = self.ui.Xdpi.value()
        #self.dpiY = self.ui.Ydpi.value()
        self.CalibX = self.ui.bedXorigin.value()
        self.CalibY = self.ui.bedYorigin.value()
        self.BedsizeX = self.ui.bedXaxis.value()
        self.BedsizeY = self.ui.bedYaxis.value()
        self.jetFreq = self.ui.jet_freq.value()
        self.motorXResln = self.ui.xmotionresln.value()
        self.motorYResln = self.ui.ymotionresln.value()
        
    def layervalue(self):
        self.ui.layernum.setText("layer " +str(self.ui.layernumb.value()) + "/" + str(self.image_converter.get_model_layers_numb()))
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
            image_to_send = self.image_converter.getlayer(image_numb)
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
    def image_draw(self):
       
        self.ax.imshow(image_to_send[0:self.count,0:self.count],origin='upper', aspect='auto')
        self._canvas.draw()
        self.count = self.count +5
        
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Silc3r SVG File", r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES',"SVG Files (*.svg);;All Files (*)", options=options)
        if fileName:
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Model Found & processed</span>')
            #print(fileName)
            self.done_data = False
            self.ui.print.setEnabled(False)
            modelname = fileName.split("/")[-1]
            modelname = modelname.split(".")[0]
            self.ui.modelname.setText(modelname)
            #return fileName
            self.model_layers =[]
            self.image_converter.openfile(fileName)
            self.model_layers = self.image_converter.get_model_layers()
            layer_numbers = self.image_converter.get_model_layers_numb()
            #self.ui.verticalSlider.setEnabled(True)
            self.ui.layernumb.setEnabled(True)
           # self.ui.verticalSlider.setRange(0,layer_numbers)
            self.ui.layernumb.setMaximum(layer_numbers)
            
            self.ax2 = self.draw3d(self.ax2,layer_numbers)
            self.ax1 = self.draw2d(self.ax1,0)
            self._canvas1.draw()
            self._canvas2.draw()
            #self.ui.verticalSlider.valueChanged['int'].connect(partial(self.draw2d,self.ax1,self.ui.verticalSlider.value()))
           # self.ui.verticalSlider.valueChanged['int'].connect(self.update_2d )
            self.ui.layernumb.valueChanged.connect(self.update_2d)
            #self.ui.verticalSlider.valueChanged['int'].connect(self.ui.layernumb.setValue(self.ui.verticalSlider.value()))
            #self.ui.verticalSlider.setEnabled(True)
           # self.disp_layers(0)
    def Printer_disconnected(self):
        #disconnect printer
        # code to be written here to disconnect printer
        #
        self.ui.label_3.setText("Disconnected")
        self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">Printer is Disconnected</span>')
        #self.ui.textBrowser.setText('<span style="color:darkolivegreen;font-weight:bold">Printer is Disconnected</span>')
        
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
        print(layer_value)
        
        self.ax1 = self.draw2d(self.ax1,layer_value)
       
        self._canvas1.draw()
        #self.ui.layernumb.setValue(layer_value)
        
        
        
    
           
    def create_fig(self,proj,xlim,ylim):
        #sns.set()
        plt.style.use('seaborn')
        self._canvas = FigureCanvas(Figure(figsize=(8.7,5.3),dpi =100))
        
        if(proj == "2d"):
             self.ax = self._canvas.figure.add_subplot(111)
             
             self.ax.set_xlim([0, xlim]) #2125
             self.ax.set_ylim([0, ylim]) #2125
      #  self.ax.set_zlim([0,30])
             major_ticks = np.arange(0, xlim, 100)
             minor_ticks = np.arange(0, ylim, 5)

             self.ax.set_xticks(major_ticks)
             self.ax.set_xticks(minor_ticks, minor=True)
             self.ax.set_yticks(major_ticks)
             self.ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
             self.ax.grid(which='both')

        # Or if you want different settings for the grids:
             self.ax.grid(which='minor', alpha=0.2)
             self.ax.grid(which='major', alpha=0.5)
             self._canvas.figure.tight_layout()
             self._canvas.move(-50,-30)
             return self._canvas,self.ax
         
        if(proj == "3d"):
             self.ax = self._canvas.figure.add_subplot(111,projection ='3d')
             self.ax.set_xlim([0, xlim]) #2125
             self.ax.set_ylim([0, ylim]) #2125
             self.ax.set_zlim([0,30])
             major_ticks = np.arange(0, xlim, 100)
             minor_ticks = np.arange(0, ylim, 5)

             self.ax.set_xticks(major_ticks)
             self.ax.set_xticks(minor_ticks, minor=True)
             self.ax.set_yticks(major_ticks)
             self.ax.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
             self.ax.grid(which='both')

        # Or if you want different settings for the grids:
             self.ax.grid(which='minor', alpha=0.2)
             self.ax.grid(which='major', alpha=0.5)
             self._canvas.figure.tight_layout()
             self._canvas.move(-50,-30)
             return self._canvas,self.ax
         
    def draw3d(self,axes,layers):
            axes.clear()
            for j in range(0,layers):
                layer_data =  self.image_converter.getlayer_data(j)
                for i in range(0,len(layer_data)):
                    
                    path = Path(layer_data[i])
                    patch = patches.PathPatch(path)
                    axes.add_patch(patch)
                    art3d.pathpatch_2d_to_3d(patch, z=j, zdir='z')
                    
            ylim = self.image_converter.img_getheight() +100
            xlim = self.image_converter.img_getWidth() + 100
            axes.set_xlim([0, xlim]) #2125
            axes.set_ylim([0, ylim]) #2125
            axes.set_zlim([0,layers + 10])
            major_ticks = np.arange(0, xlim, 100)
            minor_ticks = np.arange(0, ylim, 5)

            axes.set_xticks(major_ticks)
            axes.set_xticks(minor_ticks, minor=True)
            axes.set_yticks(major_ticks)
            axes.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
            axes.grid(which='both')

        # Or if you want different settings for the grids:
            axes.grid(which='minor', alpha=0.2)
            axes.grid(which='major', alpha=0.5)
            return axes
    def draw2d(self,axes,layer):
        axes.clear()
        layer_data =  self.image_converter.getlayer_data(layer)
        for i in range(0,len(layer_data)):
            path = Path(layer_data[i])
            patch = patches.PathPatch(path)
            axes.add_patch(patch)
        ylim = self.image_converter.img_getheight() +100
        xlim = self.image_converter.img_getWidth() + 100
        axes.set_xlim([0, xlim]) #2125
        axes.set_ylim([0, ylim]) #2125
            
        major_ticks = np.arange(0, xlim, 100)
        minor_ticks = np.arange(0, ylim, 5)

        axes.set_xticks(major_ticks)
        axes.set_xticks(minor_ticks, minor=True)
        axes.set_yticks(major_ticks)
        axes.set_yticks(minor_ticks, minor=True)

        # And a corresponding grid
        axes.grid(which='both')

        # Or if you want different settings for the grids:
        axes.grid(which='minor', alpha=0.2)
        axes.grid(which='major', alpha=0.5)
        
        return axes
        
    
#if __name__.endswith('__main__'):
    #m = Main_PROGRAM()
   # m.link_ui()
if __name__=='__main__':
		
		app = QtWidgets.QApplication(sys.argv)
		
		
		m = Main_PROGRAM()

		
		app.aboutToQuit.connect(m.close_connection)
		app.exec_()
		#sys.exit(app.exec_())
    #app.aboutToQuit.connect(sys.exit(app.exec_()) )
   #m.MainWindow.show()
#   if app.exec_() ==0 and m.check_connection == True:
#      
#       m.close_connection()
#       print("closed")
       
    