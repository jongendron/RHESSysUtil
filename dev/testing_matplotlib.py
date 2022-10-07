# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 12:25:31 2022

@author: PETBUser
"""
#%% Load Dependencies
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
# %matplotlib

# Plotting Settings
plt.style.use('classic')

#%% Plotting from script
x = np.linspace(0, 10, 100)

plt.plot(x, np.sin(x))
plt.plot(x, np.cos(x))

plt.draw()
# plt.show() # should only be used once per python session

#%% 


