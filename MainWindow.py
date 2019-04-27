# -*- coding: utf-8 -*-

""" This file is for Main program GUI and linking of Other Project files
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
import sys

## for icon:
from PyQt5 import QtGui 
from PyQt5.QtCore import QRect

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.title = "3DP"
        self.top = 100
        self.left = 100
        self.width = 500
        self.height = 500
        
        self.InitWindow()
        
        
    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.setWindowIcon(QtGui.QIcon("mjp-multijet-printing.jpg"))
        #self.setWindowIcon(QtGui.QIcon("binder_jetting_1765.png"))
        #self.setWindowIcon(QtGui.QIcon("3dp.jpg"))
        
        #self.next_layer_button = QPushButton("Next layer",self)
        self.UiComponents()
        self.show()
        
        #self.next_layer_button.clicked.connect(lambda:print("clicked"))
         
    def UiComponents(self):
        next_layer_button = QPushButton("Next layer",self)
        next_layer_button.setGeometry(QRect(100,100,100,30))
        
        
App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())