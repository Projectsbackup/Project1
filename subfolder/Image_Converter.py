# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 17:05:50 2019

@author: MG
"""

import os
from PyQt5.QtGui import QPixmap, QColor, QImage
from PyQt5 import QtCore
from numpy import *
import numpy as np
import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
from matplotlib.path import Path
#from PIL import Image, ImageDraw

from matplotlib.colors import ListedColormap
import time  # for testing 
import cv2
"""Class Image_Converter 
Converts Slic3r SVG file into stack of images 
representing each layer of STL/CAD model to print
"""

class Image_Converter():
    def __init__(self):
        super().__init__()
        
        self.file_type =0  # 0  no file , 1 svg file type, for later more than 1 file type.
        self.file_path =''
        self.image_height = 0
        self.image_width =0
        self.dpiY = 185
        self.dpiX = 329 # 77 microns in X axis motion
        self.layers = []
        self.bedpreview = []
        self.layers_data = []
        self.layer_info = []
    
    def setdpiX(self,dpX):
        self.dpiX = dpX
    def setdpiY(self,dpY):
        self.dpiY = dpY
    def openfile(self,temp_file_path):
        "try to open a file if success return 1 , if fail return 0"
        temp_success =0   # if file is successfully opened or not , 0 not 1 opened
        self.layers =[]
        self.layers_data =[]
        if(str(temp_file_path)==""):
            self.file_type =0
           # print("File Directory is not given")
            return 0;
        if(os.path.exists(str(temp_file_path)) ==False):
           # print("The File directory doesn't exist")
            return 0;
        else:
            self.file_path = temp_file_path
            filename,file_extension = os.path.splitext(temp_file_path)
            if(file_extension.lower() != ".svg"):
              #  print("File type/extension is not compatible NOT an SVG File from Slic3r Program")
                return 0
            
            if(file_extension.lower() == ".svg"):
                self.file_type =1
            try:
                with open(self.file_path) as file_object:
                    self.vector_file = file_object.read()
                temp_success =1
            except:
                nothing =0
            if(temp_success ==1):
              #  print("file opened")
               # print(self.vector_file)
                self.SVG2data(self.file_path)
                return 1
                #self.SVG_getdata()
    
    def get_model_layers(self):
        return self.layers
    
    def get_model_layers_numb(self):
       # return len(self.layers)    #changed
        return len(self.layers_data)
    
    def Bed_image(self):
       bed_height = math.floor(150 * (self.dpiX/25.4)) #150mm * 200 dpi/25.4 inch>mm
       bed_width = math.floor(150 * (self.dpiY/25.4))
       bed_image = zeros((bed_height,bed_width))
       return bed_image
    
    def CadModelDim(self,h,w):
        self.h = h
        self.w = w
        
    def getCadModelDim(self):
        return self.h,self.w
    def SVG2data(self,filename):
        et = ET.ElementTree(file = filename)
        self.height = float(et.getroot().get('height'))
        self.width =  float(et.getroot().get('width'))
        self.CadModelDim(self.height,self.width)
       # self.height = int((self.height)* (self.dpi/25.4)) +1
       # self.width = int((self.width)* (self.dpi/25.4)) +1
        self.height = int((self.height)* (self.dpiY/25.4)) +1    # was 360/25.4
        if(self.height % 128  !=0):
           # print("height0 %d",(self.height))
            self.height = 128 * math.ceil(self.height/128)
          #  print("height %d",(self.height))
       # self.width = int((self.width)* (339/25.4)) +1    #old resolution = 185 , adjust dpi  in polygonarray as well
        self.width = math.ceil((self.width)* (self.dpiX/25.4)) + (2+(5*42) )#was 339/25.4 , 5 steps each 3 nozzles * (126/3 = 42) + last nozzle (+2)  
        self.image_height = self.height
        self.image_width = self.width
        image = zeros((self.height,self.width) )
        
        #print(self.height,self.width)
        total_layers = 0
        #print( len(et.getroot()[1]))
        for i in et.findall("{http://www.w3.org/2000/svg}g"):
            total_layers= total_layers+1
       # print(total_layers)
        
       # image0 = zeros(self.image_height,self.image_width)
        img = np.zeros((self.height,self.width) )
        nr, nc = img.shape
        ygrid, xgrid = np.mgrid[:nr, :nc]
        self.xypix = np.vstack((xgrid.ravel(), ygrid.ravel())).T
        self.totalLayer_shape = []
        for j in range(0,total_layers-1): #total_layers
            imagex = np.zeros((self.height,self.width) )
          #  total_bedpreview = []
            self.layer_info = []
            self.layer_shape =[]
            
           # imagex =self.Bed_image()
            for i in range(0,len(et.getroot()[j])):
               # shape_type = et.getroot()[j][i].attrib  # for extracting attribss
                first_g =  et.getroot()[j][i].get('points')
                shape_type = et.getroot()[j][i].get('{http://slic3r.org/namespaces/slic3r}type')
                if(shape_type == "hole"):
                    shape =0
                else:
                   shape =1 
               # print(shape_type)
                first_g =first_g.replace(' ',',')
                first_g2 = np.fromstring(first_g,sep=',').reshape(-1,2)
               # total_bedpreview.extend(first_g2)
                imagex =imagex +self.polygon2img(imagex,first_g2,shape)
                
                self.layer_shape.append(shape)
#               
               
            #imagex = zeros((self.height,self.width) )
            #imagex =self.polygon2img(imagex,first_g2)
            
            #bed_image = bed_image + imagex
            self.totalLayer_shape.append(self.layer_shape)
            self.layers_data.append(self.layer_info)
            
           # self.bedpreview.append(total_bedpreview)
            #self.layers.append(imagex)
            
        #self.showlayers(self.layers)
        #print(len(self.layers))  
       # print((self.bedpreview[0][0][0]))
    def get_totalLayer_shape(self,layernum):
        l = self.totalLayer_shape[layernum]
        return l
    def poly2imgWrite(self,layer,layer_data_type):
        img =0
        #imge = np.zeros((self.img_getheight(),self.img_getWidth()),dtype=np.int32 )
        for i in range(0,len(layer)):
           # pth = Path(layer[i])
            imge = np.zeros((self.img_getheight(),self.img_getWidth()),dtype=np.int32 )
            start = time.time()
            shape = layer_data_type[i]
            if shape ==0:
                cv2.fillPoly( imge, np.int32([layer[i]]), -1 )
            else:
                cv2.fillPoly( imge, np.int32([layer[i]]), 1 )
#    cv2.fillPoly( im, a3, 255 )
#
#    plt.imshow(im)
#    plt.show()

           # mask = pth.contains_points(xypix)
            end = time.time()
           # print(end - start)
            mask =0
            shape = layer_data_type[i]
            if shape ==0:
                mask = mask*-1
                #imge = imge*-1
           # mask = mask.reshape(self.height,self.width)
            img = img + imge
        
           
       # plt.imshow(img, cmap='Blues') #interpolation='nearest'
       # plt.show()
        return img
    def polygon2img(self,img,polygonarraypoints,shape):
#        nr, nc = img.shape
#        ygrid, xgrid = np.mgrid[:nr, :nc]
#        xypix = np.vstack((xgrid.ravel(), ygrid.ravel())).T
       # print(xypix)
       # polygonarraypoints = polygonarraypoints * (self.dpi/25.4)
        #self.layer_info.append(polygonarraypoints.astype(int))
        polygonarraypoints[:,0] = polygonarraypoints[:,0] * (self.dpiX/25.4)  #was 339/25.4
       
        polygonarraypoints[:,1] = polygonarraypoints[:,1] * (self.dpiY/25.4)  #was 360/25.4
        self.layer_info.append(polygonarraypoints.astype(int))
        
        #print(polygonarraypoints)
       # pth = Path(polygonarraypoints)
       # mask = pth.contains_points(self.xypix)
        
        mask =0
        if(shape == 0):
            mask = mask * -1
       # print(mask.shape)
       # mask = mask.reshape(img.shape)
       # print(shape)
       

        return mask
    
        
    def showlayers(self,layers):
        for l in range(len(layers)):
            
            data = layers[l]
            #print(data)
            
            #plt.ion()
            #plt.figure()
            plt.imshow(data, cmap=plt.cm.gray) #interpolation='nearest'
            plt.show()
           # input("press any key to continue")
           # plt.close()
    def img_getheight(self):
       return self.image_height
   
    def img_getWidth(self):
       return self.image_width
   
    def getlayer(self,layer_required):
        if(len(self.layers) <1):
            return ("no layers were found")
        else:
            return self.layers[layer_required]
    
    def getlayer_data(self,layerinfo_required):
        if(len(self.layers_data) <1):
            return ("no layers were found")
        else:
            return self.layers_data[layerinfo_required]
   
if __name__.endswith('__main__'):
    im = Image_Converter()
   # ret = im.openfile('../../../ExampleSVGfiles\sphere.svg')
   
   # ret = im.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\spheresmaller5x.svg')
    ret = im.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\test.svg')
    print(ret)
    print("finished")
    
    img = np.zeros((im.img_getheight(),im.img_getWidth()) )
    nr, nc = img.shape
    ygrid, xgrid = np.mgrid[:nr, :nc]
    xypix = np.vstack((xgrid.ravel(), ygrid.ravel())).T
    #start = time.time()
    loc =r"\Layer_data"
    if len(os.listdir(os.getcwd()+loc) ) == 0:
        start = time.time()
        ia =im.poly2imgWrite(im.getlayer_data(i),im.get_totalLayer_shape(0))
        np.savetxt(loc+"\Image"+str(i) +".txt",ia, fmt = '%d',delimiter=',',newline ='\n',header ='[',footer =']')
        end1 = time.time()
        print("Generating Model data of %d layers, Estimated Time: %d seconds" % (im.get_model_layers_numb(),(end1-start)*im.get_model_layers_numb()) ) 
        for i in range(0,im.get_model_layers_numb()):
            ia =im.poly2imgWrite(im.getlayer_data(i),im.get_totalLayer_shape(i))
            np.savetxt(loc+"\Layer"+str(i) +".txt",ia, fmt = '%d',delimiter=',',newline ='\n',header ='[',footer =']')
    else:
        print("please Empty the 'Layer_data' folder in the program directory")
    #end = time.time()
    #ia = im.poly2imgWrite(im.getlayer_data(1),im.get_totalLayer_shape(1))
    
    
    #np.savetxt(loc+"\Image"+str(1) +".txt",ia, fmt = '%d',delimiter=',',newline ='\n',header ='[',footer =']')
    end = time.time()
    #print(im.img_getheight())
    print("time taken" + str(end-start))
    #print(im.Bed_image())
   # im.showlayers(im.get_model_layers() )
   # print(im.getlayer_data(10))
    #im.showlayers(im.getlayer_data(10) )
   # print(im.getlayer(1))
   # im.showlayers(im.get_model_layers())
    #test = im.getlayer(10)
   