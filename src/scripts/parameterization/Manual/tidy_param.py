# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:33:22 2022

@author: jonge
"""

#%% Import RHESSysUtil Modules by editing System path to include rhessys_util
import sys, os
# tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir, 'rhessys_util'))
tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir))
tar_dir = r"{}".format(tar_dir)
sys.path.append(tar_dir)
#import rhessys_util
from rhessys_util import extract, tidy, analyze, visual, util

import numpy as np
import pandas as pd

#%% Define the tidy_param function
def tidy_param():
    print("Start of tidy_param()")

#%% Call the main function if this is the main script
if __name__ == '__main__':
    tidy_param()

#%% End
print("End of tidy_param()")