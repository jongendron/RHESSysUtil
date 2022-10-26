# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:33:22 2022

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

from rhessys_util import tidy

#%% Define the tidy_param function
def tidy_param(Data: dict, Agg: bool, Agg_grp1: list, Agg_grp2: list, Agg_method: list, Rollmean: bool = False, Rollmean_k: int = 3) -> dict:
    """
    Manipulates all RHESSys datasets provided by input `Data`. Available manipulation
    methods include:
        (1) Aggregation - Computes statistics to upscale data based on `Agg_grp1`,
        `Agg_grp2`, and `Agg_method`. Uses functions from rhessys_util.tidy.
        
    Parameters
    ----------
    Data : dict
        Object that stores data to be manipulated.Each dict item should correspond 
        to a unique RHESSys output variable, and should be in Pandas Dataframe format.
        For required input format, see the `extract_param.py`.
        
    Agg : bool, optional
        Switch that specifies whether aggregation will be conducted.
    Agg_grp1 : list
        List of columns to group each dataset by during first stage of aggregation.
    Agg_grp2 : list
        List of columns to group each dataset by during second stage of aggregation.
    Agg_method : list
        List of size two specifying method to use for aggregation stages 1 and 2.
        For valid option, see rhessys_util.tidy.format_agg()
    Rollmean : bool
        Switch the specifies whether to get a rolling mean of the time series data,
        based on the window `Rollmean_k`.
    Rollmean_k : int
        Size of the rolling mean window.

    Returns
    -------
    dict
        Updated dictionary with same keys as the input `Data`, but with modified
        datasets from this function.

    """
    print("Start of tidy_param()")       
    #%% Apply aggregation
    vdict = Data.copy()
    
    # Time_spat = non data columns (not the target for aggregation, rollmean, ... etc)
    time_spat = ['date', 'dec', 'year', 'month', 'day'] # any time scale
    time_spat = time_spat + ['sdec', 'syr', 'smth', 'sday'] # any simtime
    # TODO: Automate time_spat so it will grab any col where the last two characters are 'id' as well as the time 
    time_spat = time_spat + ['basinid', 'hillslopeid', 'hillid', 'zoneid', 'patchid', 'stratumid', 'vegid','id', 'veg_parm_id'] 
                                  
    if Agg == True:
        for var in vdict.keys():
            
            # vlist = [item for item in vdict[var].columns if item.isnumeric()] # only if data columns are garanteed numbers
            vlist = [item for item in vdict[var].columns if item not in time_spat]
            vdict[var] = tidy.agg(Dataframe=vdict[var], 
                                         Varlist=vlist, 
                                         Group1=Agg_grp1, 
                                         Group2=Agg_grp2, 
                                         Method=Agg_method
                                         )
    
    if Rollmean == True:
        for var in vdict.keys():
            # vlist = [item for item in vdict[var].columns if item.isnumeric()] # only if data columns are garanteed numbers
            vlist = [item for item in vdict[var].columns if item not in time_spat]
            vdict[var] # = tidy.apply_rollmean()

    print("End of tidy_param()", '\n'*2)
    return vdict                    

#%% Call the main function if this is the main script
if __name__ == '__main__':
    print("Start of tidy_param()")
    tidy_param()
    print("End of tidy_param()")