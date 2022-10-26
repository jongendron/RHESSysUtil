# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:31:00 2022

Imports program settings from external file.

@author: jonge
"""

#%% Import Dependencies
import numpy as np
import pandas as pd

#%% Import Dependencies from RHESSysUtil Modules by editing System path to include rhessys_util
import sys, os
# tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir, 'rhessys_util'))
tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir))
tar_dir = r"{}".format(tar_dir)
sys.path.append(tar_dir)

from rhessys_util import util # determine which modules required

#%% Define the import_param function
def import_param(File):
    print()
    

#%% Call the main function if this is the main script
if __name__ == '__main__':
    print("Start of import_param()", '\n')
    import_param()
    print("End of import_param()", '\n')