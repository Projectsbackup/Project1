# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import sys
from PyQt5.QtGui import QPixmap, QColor, QImage
from Image_Converter import Image_Converter
from Ui_MainWindow import Ui_MainWindow

from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
import subprocess

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
import os

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
          
         self.link_ui()
         
         
         
    def link_ui(self):
        #ret = self.image_converter.openfile('../../../ExampleSVGfiles\sphere.svg')
        
#        ret = self.image_converter.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\spheresmaller5x.svg')
#        self.model_layers = self.image_converter.get_model_layers()
#        print('layers:{}'.format(len(self.model_layers)))
#        imagex = self.model_layers[0]
#        imagex = np.uint8(imagex)
#       # img = Image.fromarray(imagex.data, 'I')
#        #img.save('my.png')
#       # np.set_printoptions(threshold=np.inf)
#        print(imagex)
#        
#       # plt.imshow(imagex) #interpolation='nearest'
#       # plt.show()
#        imagex2 = imagex*255
#        image = QtGui.QImage(imagex2.data, imagex2.shape[1],
#                             imagex2.shape[0] ,imagex2.shape[1],QtGui.QImage.Format_Indexed8)
#        pix = QtGui.QPixmap(image)
#        
#        '''Saving and Making PIL IMAGE '''
#        #img = Image.fromarray(imagex2, 'L')
#        #img.save('my.png')
#        
#       # pix = QPixmap().loadFromData(img)
#        pix = QPixmap().fromImage(image)
        #self.ui.layer.setPixmap(pix)
        #self.ui.layer.setPixmap(QtGui.QPixmap('3dp.jpg') )
        #self.ui.layer.setPixmap(QtGui.QPixmap(img) )
        
        #self.ui.Next_layer.clicked.connect(lambda:self.increase_display_counter() )
        print("x")
        #self.ui.verticalSlider.setRange(0,len(self.model_layers)-1) #changed
        self.ui.verticalSlider.valueChanged['int'].connect(self.disp_layers)
        #self.display_curr_layer(len(self.model_layers),self.display_layer_counter)
        self.ui.pushButton.clicked.connect(self.openSlic3r)
        
        self.ui.openGLWidget.initializeGL
       # self.ui.openGLWidget.initializeGL = self.initializeGL()
       # self.draw()
        self.ui.tabWidget.currentChanged['int'].connect(self.tabSelected) 
        
       # self.ui.previous_layer.clicked.connect(lambda:self.ui.label_3.setText("Disconnected"))
        self.ui.previous_layer.clicked.connect(self.Printer_disconnected)
        #self.ui.label_3.setText("Disconnected")
        self.ui.pushButton_3.clicked.connect(self.openFileNameDialog)
        
    
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES',"SVG Files (*.svg);;All Files (*)", options=options)
        if fileName:
            self.ui.textBrowser.append('<span style="color:darkolivegreen;font-weight:bold">File Found</span>')
            print(fileName)
            #return fileName
            self.model_layers =[]
            self.image_converter.openfile(fileName)
            self.model_layers = self.image_converter.get_model_layers()
            self.ui.verticalSlider.setRange(0,len(self.model_layers)-1)
            self.disp_layers(0)
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
    def tabSelected(self, arg=0):
        print(arg)
        if(arg ==0):
            self.draw()
   
    def draw(self):
       # self.ui.openGLWidget.initializeGL()
        #self.ui.openGLWidget.initializeGL = self.initializeGL()
        self.ui.openGLWidget.paintGL = self.paintGL
        #self.ui.openGLWidget.repaint()
        
    def disp_layers(self,layer_no):
        if not self.model_layers:
            pass
        else:
            imagex = (np.uint8(self.model_layers[layer_no]) ) * 255
            image1 = QtGui.QImage(imagex.data, imagex.shape[1],
                                  imagex.shape[0] ,imagex.shape[1],QtGui.QImage.Format_Indexed8)
            pix1 = QtGui.QPixmap(image1)
            self.ui.layer.setPixmap(pix1.scaled(self.ui.layer.width(),self.ui.layer.height(), QtCore.Qt.KeepAspectRatio))
    
    def increase_display_counter(self):
        self.display_layer_counter= self.display_layer_counter +1
        print(self.display_layer_counter)
        self.display_curr_layer(len(self.model_layers),self.display_layer_counter)

    def display_curr_layer(self,total_layers,layer_counter):
        #print(layer_counter)
        if layer_counter in range(0,total_layers):
            #print(layer_counter)    
            imagex = (np.uint8(self.model_layers[layer_counter]) ) * 255
            image1 = QtGui.QImage(imagex.data, imagex.shape[1],
                                  imagex.shape[0] ,imagex.shape[1],QtGui.QImage.Format_Indexed8)
            pix1 = QtGui.QPixmap(image1)
            self.ui.layer.setPixmap(pix1.scaled(self.ui.layer.width(),self.ui.layer.height(), QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
           # self.paintGL(image1)
           # self.ui.openGLWidget.paintGL = self.paintGL(image1)
    #Comment Color code :#adadad
    #OPENGL PART funcs
    def paintGL(self):
        self.loadScene()
        vertices = []
       # self.ui.openGLWidget.convertToGLFormat(img)
      #  glut.glutWireSphere(2, 13, 13)
        #glut.glutSolidSphere(2,13,13)
#        vertices = [-10, -10,2,   0.0, 10,4,   10, -10,6]    
#        
#        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, vertices)
#        gl.glEnableVertexAttribArray(0)
#        gl.glColor(0,0,0)
#        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)   
#        
#        gl.glDisableVertexAttribArray(0)   
        for x1 in range(0,150,1):
            for y1 in range(0,150,1):
                x2 = x1 + 1
                y2 = y1 + 1
                #vertices.extend([x1,y1,x2,y1,x2,y2,x1,y2])
                #vertices.extend([x1,y1])
                self._gl_set_color(gl.GL_FRONT_AND_BACK, [0.2, 0.2, 0.7, 0.3], shininess=0.75)
                gl.glBegin(gl.GL_LINE_LOOP)
                gl.glVertex3fv([x1, y1, 0])
                gl.glVertex3fv([x2, y1, 0])
                gl.glVertex3fv([x2, y2, 0])
                gl.glVertex3fv([x1, y2, 0])
                gl.glEnd()
                
#                self._gl_set_color(gl.GL_FRONT_AND_BACK, [0.2, 0.2, 0.7, 0.3], shininess=0.75)
#                gl.glBegin(gl.GL_LINE)
#                gl.glVertex3fv([x1+5, y1+5, 0])
#                gl.glVertex3fv([x1+10, 150, 0])
#                #gl.glVertex3fv([x2, y2, 0])
#               # gl.glVertex3fv([x1, y2, 0])
#                gl.glEnd()
#        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, vertices)
#        gl.glEnableVertexAttribArray(0)
#        gl.glColor(1,1,1)
#        gl.glDrawArrays(gl.GL_LINE_LOOP, 0, len(vertices)-1)
#        gl.glDisableVertexAttribArray(0)
        print("hena")
    
    def _gl_set_color(self, side, color, shininess=0.33):
        gl.glMaterialfv(side, gl.GL_AMBIENT_AND_DIFFUSE, color)
        gl.glMaterialfv(side, gl.GL_SPECULAR, color)
        gl.glMaterialf(side, gl.GL_SHININESS, int(127*shininess))
        gl.glColor4fv(color)    
    def initializeGL(self):
        print("\033[4;30;102m INITIALIZE GL 2 \033[0m")
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_DEPTH_TEST)

    def loadScene(self):
        gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glViewport(0, 0, self.ui.openGLWidget.width(), self.ui.openGLWidget.height())
        x, y, width, height = gl.glGetDoublev(gl.GL_VIEWPORT)
#        glu.gluPerspective(
#            90,  # field of view in degrees
#            width / float(height or 1),  # aspect ratio
#            .25,  # near clipping plane
#            200,  # far clipping plane
#        )
        gl.glOrtho(-2,152,-2,152,-1,1)
        #gl.glOrtho(-1,16,-1,16,-1,1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
       # gl.glTranslatef(-50,-20,-50)
       # gl.glRotatef(40,1,1,0)
        #glu.gluLookAt(12, 12, 90, 0, 0, 0, 0, 1, 0)
       # glu.gluLookAt(0, 90, 90, 0, 90, 80, 0, 1, 0)
       # glu.gluLookAt(0, 0, 0, 0, 0, 0, 0, 0, 1)
        background = [.99, .99, .99, 1.0]
#        # if user passed a background color use it
#        if 'background' in self.kwargs:
#            try:
#                # convert to (4,) uint8 RGBA
#                background = to_rgba(self.kwargs['background'])
#                # convert to 0.0 - 1.0 float
#                background = background.astype(np.float64) / 255.0
#            except BaseException:
#                log.error('background color wrong!',
#                          exc_info=True)
#        gl.glClearColor(*background)

if __name__ == '__main__':
    #m = Main_PROGRAM()
   # m.link_ui()
   app = QtWidgets.QApplication(sys.argv)
   m = Main_PROGRAM()
   #m.MainWindow.show()
   sys.exit(app.exec_())