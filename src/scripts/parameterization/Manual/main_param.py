# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:41:40 2022

@author: jonge
"""

#%% Imports Using relative paths
# import numpy as np
#import pandas as pd
# from ....rhessys_util import extract, tidy, analyze, visual, util

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
#%% Define the main function
def main():
    """
    Manual parameterization program; calls on modules `extract`,
    `tidy`, `analyze`, and `visual`. Together this program does the following:
        (1) Extracts RHESSys output data from a directory of output files.
        (2) Formats the data into dataframes (one for each variable).
        (3) Conducts statistical analysis of each variable specified.
        (4) Plots the variables as requested.
        
    Settings for all modules are imported from a single file. For more information,
    refer to the documentation within each individual module.
    
    Returns
    -------
    None.

    """
    print("hello")
    
    # Read input settings file (script in same dir)
    
    # Extract data (script in same dir)
    
    # Tidy data (script in same dir)
    
    # Analyze data (script in same dir)
    
    # Visualize data (script in same dir)

#%% Call the main function if this is the main script
if __name__ == '__main__':
    main()

#%% End
print("End of main()")