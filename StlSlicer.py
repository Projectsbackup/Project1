# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 22:46:27 2019

@author: Jimmy
"""
import stl
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import math
import subprocess

# Create a new plot
figure = pyplot.figure()
axes = figure.add_subplot(111,projection ='3d') #mplot3d.Axes3D(figure)

# Load the STL files and add the vectors to the plot
#your_mesh = mesh.Mesh.from_file('Stl_Models/xaar mount tilted 31degs.stl')
your_mesh = mesh.Mesh.from_file('Stl_Models/combined.stl')
#your_mesh.x = your_mesh.x *5

#your_mesh.x = your_mesh.x + 50
#your_mesh.y = your_mesh.y + 50

print(your_mesh.max_)
print(your_mesh.min_)

#your_mesh.rotate(p, math.radians(40))
#your_mesh.rotate([0.5, 0.0, 0.0], math.radians(-90))
#your_mesh.x = your_mesh.x +50
#your_mesh.y = your_mesh.y +50
#your_mesh.z = your_mesh.z +50

your_mesh.x = your_mesh.x +(0.0-(your_mesh.x/2))
your_mesh.y = your_mesh.y +(0.0-(your_mesh.y/2))
your_mesh.z = your_mesh.z +( 0.5-(your_mesh.z/2))
    
#your_mesh.rotate([0.0,0.0,5],math.radians(-40))

your_mesh.x = your_mesh.x +(0.0+(your_mesh.x/2))
your_mesh.y = your_mesh.y +(0.5+(your_mesh.y/2))
your_mesh.z = your_mesh.z +( 0.5+(your_mesh.z/2))
  
#your_mesh.z = your_mesh.z *20 
axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors))



# Auto scale to the mesh size

scale = your_mesh.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()

your_mesh.save('Stl_Models\combined.stl', mode=stl.Mode.ASCII)
#process =subprocess.call('"C:\Program Files\Repetier-Host\Slic3r\Slic3r-console" --export-svg "Stl_Models/xaar mount tilted 31degs.stl" --layer-height 0.2 -o Stl_Models/test.svg', shell=True)

#process 0 means success ,1 not 
#print(process)