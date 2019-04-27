# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 18:59:32 2019

THIS FILE IS RESPONSIBLE FOR 2D & 3D VISUALIZATION OF THE INPUT LAYER DATA 

@author: Jimmy
"""

import matplotlib.animation as manimation
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as M3
import mpl_toolkits.mplot3d.art3d as art3d



from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path
import matplotlib.patches as patches

import numpy as np
from Image_Converter import Image_Converter

class visualization():
    def __init__(self):
        super().__init__()
        self.dpi =100
        
    def create_fig(self,proj,xlim,ylim):
        sns.set()
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
    
    def draw3d(self,fig,axes,layers):
        for j in range(0,len(layers)):
            layer_data =  im.getlayer_data(j)
            for i in range(0,len(layer_data)):
                
                path = Path(layer_data[i])
                patch = patches.PathPatch(path)
                axes.add_patch(patch)
                art3d.pathpatch_2d_to_3d(patch, z=j, zdir='z')
        return fig,axes

# if __name__.endswith('__main__'):            # __name__ =='__main__':
   # im = Image_Converter()
  # # ret = im.openfile('../../../ExampleSVGfiles\sphere.svg')
   
   # ret = im.openfile(r'C:\Users\Jimmy\Desktop\3D Printing research\Silcers\Slic3r\STL SAMPLES\spheresmaller5x.svg')
   # print(ret)
   # #print(im.Bed_image())
   # vis = visualization()
   
   # fig,ax = vis.create_fig("3d",im.img_getheight(),im.img_getWidth())
   # fig,ax = vis.draw3d(fig,ax,im.get_model_layers())
   # fig.draw()
   
        
        