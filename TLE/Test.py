from TLEParsing import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#Open TLE file
file = open('TLE/TLE 100 or so brightest 2022 Oct 24 12_05_27 UTC.txt', 'r')
Lines = file.readlines()

#Open plot
fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(111, projection='3d')

#Parse lines to grab TLE 1 at a time
i=0
while i < len(Lines):
    
    #Ignore name line and grab 2 next lines
    TLE = Lines[i+1] + Lines[i+2]
    
    #Convert in x,y,z
    x,y,z = transformTLEinXYZ(TLE)
    
    #Plot
    ax.scatter(x, y, z)
    
    #Increment
    i += 3

#Draw earth for reference
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
r = 6370000
x = r*np.cos(u)*np.sin(v)
y = r*np.sin(u)*np.sin(v)
z = r*np.cos(v)
ax.plot_wireframe(x, y, z, color="b")

plt.show()