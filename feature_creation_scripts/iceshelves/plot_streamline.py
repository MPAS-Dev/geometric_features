#!/usr/bin/env python

import numpy
from netCDF4 import Dataset

import matplotlib.pyplot as plt

from mpl_toolkits.basemap import interp

import scipy.integrate
import scipy.ndimage.morphology as morphology

from skimage import measure

def interpVel(p,t):
  np = len(p)/2
  x = p[0:np]
  y = p[np:2*np]
  u = interp(vx,X[0,:],Y[:,0],x,y)
  v = interp(vy,X[0,:],Y[:,0],x,y)
  return numpy.append(u,v)

inFileName = 'Bedmap2.nc'
inFile = Dataset(inFileName,'r')

mask = inFile.variables['bedmap2Mask'][:,:]

inFile.close()

iceMask = numpy.logical_or(mask == 0, mask == 1)
iceMask = morphology.binary_fill_holes(iceMask)

inFileName = 'Bedmap2_ice_shelf_distance.nc'
inFile = Dataset(inFileName,'r')
iceShelfDistance = inFile.variables['iceShelfDistance'][:,:]
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]
inFile.close()

iceShelfMask = iceShelfDistance >= 0.0

iceShelfNumbers = measure.label(iceShelfMask)

shelfCount = numpy.amax(iceShelfNumbers)+1

velocityFileName = 'Bedmap2_grid_velocities.nc'
inFile = Dataset(velocityFileName, 'r')
vx = inFile.variables['vx'][:,:]*iceMask
vy = inFile.variables['vy'][:,:]*iceMask
inFile.close()

(ny,nx) = vx.shape

dx = 1e3

speed = numpy.sqrt(vx**2 + vy**2)



# integrate some streamlines back in time
p0 = [-810e3, -600e3, -285e3, -227e3, -115e3,  608e3,  -978e3, -1538e3,
       595e3, 1595e3, 2100e3, 2117e3, 2135e3, 2100e3, -1250e3,  -606e3]

p = scipy.integrate.odeint(interpVel,p0,numpy.linspace(0,-15000,1000))
np = p.shape[1]/2
x = p[:,0:np]
y = p[:,np:2*np]


# integrate other streamlines forward in time
p0 = [ 874e3,   472e3, -235e3, -1985e3, -1464e3,
      1962e3, -1518e3, -515e3,  1033e3,   780e3]

p = scipy.integrate.odeint(interpVel,p0,numpy.linspace(0,10000,1000))
np = p.shape[1]/2
x = numpy.append(x,p[:,0:np],axis=1)
y = numpy.append(y,p[:,np:2*np],axis=1)

# add Tracy-Shackleton divide manually because no appropriate streamline could be found
x = numpy.append(x,numpy.linspace(2590e3,2634e3,1000).reshape((1000,1)),axis=1)
y = numpy.append(y,numpy.linspace(-481e3,-474e3,1000).reshape((1000,1)),axis=1)

my_dpi = 72
fig = plt.figure(figsize=(nx/float(my_dpi), ny/float(my_dpi)), dpi=my_dpi)
ax = plt.Axes(fig, [0., 0., 1., 1.])
ax.set_axis_off()
fig.add_axes(ax)
plt.axis('off')


plt.plot(x,y,'k',linewidth=1)

plt.xlim([-dx*0.5*(nx+1),dx*0.5*(nx+1)])
plt.ylim([-dx*0.5*(ny+1),dx*0.5*(ny+1)])
fig.canvas.draw()
plt.savefig('streamlines.png',dpi=my_dpi)
plt.close()

