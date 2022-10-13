# -*- coding: utf-8 -*-
"""
Created on Wed Oct 12 12:45:59 2022

@author: PETBUser

@resources: https://stackoverflow.com/questions/26545897/drawing-a-colorbar-aside-a-line-plot-using-matplotlib
"""

#%% Load Dependencies
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use('seaborn-whitegrid') # style

#%% Function to add colorbar to a plot object

def lnplt_cmap(Figure: mpl.axes._subplots, 
               Axis: np.ndarray,               
               X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
               Subplot: bool = False,               
               Colmap: str = 'viridis') -> None:
    """
    Create a multi series line plot with a continous colormap legend.

    Parameters
    ----------
    Figure : mpl.axes._subplots
        Matplotlib figure to add colorbar legend to.
    Axis : np.ndarray
        Matplotlib figure axis to add plot elements to.
    X : np.ndarray
        1-D array of values to be plotted on the X-axis.
    Y : np.ndarray
        2-D array of values to be plotted on the y-axis. Each column
        series is treated as it's own series.
    Z : np.ndarray
        1-D array of continous values use to describe a parameter or
        attribute associated with each series of the dependent variable.
    Subplot : bool, optional
        If True the colorbar will be plotted on the specified subplot
        of the figure. The default is False.
    Colmap : str, optional
        Name of a valid Matplotlib colormap. The default is 'viridis'.

    Returns
    -------
    None        

    """
    
    # Test if proper input variable types
    
    if type(Figure).__name__ != 'Figure':
        print('Error: `Figure` is not `mpl.figure.Figure`')
        return 0
    
    if type(Axis).__name__ != 'ndarray' and type(Axis).__name__ != 'AxesSubplot':
        print('Error: `Axis` is not `np.ndarray`')
        return 0
    
    if type(X).__name__ != 'ndarray':
        print('Error: `X` is not `np.ndarray`')
        return 0
    
    if type(Y).__name__ != 'ndarray':
        print('Error: `Y` is not `np.ndarray`')
        return 0
    
    if type(Z).__name__ != 'ndarray':
        print('Error: `Z` is not `np.ndarray`')
        return 0
    
    if type(Colmap).__name__ != 'str':
        print('Error: `Colmap` is not `str`')
        return 0
    
    if type(Subplot).__name__ != 'bool':
        print('Error: `Subplot` is not `bool`')
        return 0
    
    reg = [item for item in mpl.colormaps()] # available colormap names
    if Colmap not in reg:
        print(f'Error: {Colmap} is not a valid colormap name in Matplotlib registry. See mplt.colormaps() for full list of available color maps.')
        return 0
    
    # Test if array shapes are correct
    if Z.shape[0] != Y.shape[1]:
        print("Error: num col in Y != length of Z")
        return 0
        
    if X.shape[0] != Y.shape[0]:
        print("Error: num rows in Y != length of X")
        return 0
    
    # norm is a class which, when called, can normalize data into the
    # [0.0, 1.0] interval.
    norm0 = mpl.colors.Normalize(vmin=np.min(Z), vmax=np.max(Z))
    
    # choose a valid matplotlib colormap ('matplotlib.colors.ListedColormap' format)    
    cmap0 = mpl.colormaps[Colmap]
    
    # create a ScalarMappable and initialize a data structure
    smap0 = mpl.cm.ScalarMappable(cmap=cmap0, norm=norm0)
    smap0.set_array([])
    
    # crate the lineplot
    nc = Y.shape[1]
    for i in range(0,nc):
        xval = X
        yval = Y[:,i]
        zval = smap0.to_rgba(Z[i])
        Axis.plot(xval, yval, c=zval)

            
    if Subplot:                
        Figure.colorbar(smap0, ax=Axis)
    else:
        Figure.colorbar(smap0)
        
    return None
    
#%% Test
nrow = 1000
ncol = 10

zv = np.linspace(-1,1, ncol)
xv = np.linspace(0,3*np.pi,nrow)        # xaxis
yv = np.cos(xv)[:,np.newaxis] # yaxis
yv = yv + zv

#%%     
fig, ax = plt.figure(), plt.axes()

lnplt_cmap(Figure=fig, Axis=ax, X=xv, Y=yv, Z=zv, Colmap='terrain')

#%% Test 2
fig, ax = plt.subplots(3)

for i in range(0,3):
    zv2 = zv + (i+1)
    lnplt_cmap(fig, ax[i],
               X=xv, Y=yv, Z=zv2, Colmap='terrain',
               Subplot=True)
    ax[i].set_title(f'Plot {i}')
    # ax[i].legend()
    
        
#%% Test 3
fig, ax = plt.subplots(2,2)

rscl = np.linspace(0,1,2) + 1
cscl = np.linspace(1,3,2)

for i in range(0,len(rscl)):
    for j in range(0,len(cscl)):
        #zv2 = zv*rscl[i] + cscl[j]
        lnplt_cmap(fig, ax[i,j],
                   X=xv, Y=yv, Z=zv, Colmap='viridis',
                   Subplot=True)
        ax[i,j].set_title(f'Plot {[i,j]}')    
