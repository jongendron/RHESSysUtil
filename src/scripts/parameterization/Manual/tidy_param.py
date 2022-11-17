# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:33:22 2022

@author: jonge
"""

#%% Import Dependencies
import numpy as np
import pandas as pd
import warnings

#%% Import Dependencies from RHESSysUtil Modules by editing System path to include rhessys_util
import sys, os
# tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir, 'rhessys_util'))
tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir))
tar_dir = r"{}".format(tar_dir)
sys.path.append(tar_dir)

from rhessys_util import tidy

#%% Define the tidy_param function
def tidy_param(Data: dict, 
               Join: bool, Join_file: str, Join_file_form: str, Join_grp: list, 
               Agg: bool, Agg_grp1: list, Agg_grp2: list, Agg_method: list, 
               Rollmean: bool = False, Rollmean_k: int = 3, Rollmean_grp: list = [None]) -> dict:
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
        
    
    Join : bool
        Switch that specifies whether to join external dataset with the target dataset.
    Join_file : str
        Path to the file that will be loaded as Pandas Dataframe and joined with target dataset.
    Join_file_form : str
        Format of `Join_file` (csv or tsv); dictates how program will read the file.
    Join_grp : list
        List of columns to join `Join_file` and the target dataset by. Columns must exists in
        both datasets.
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
    Rollmean_grp : list
        List of columns to group `Data` by before conducting Rolling mean procedure.
        The rolling mean is when obtained for all rows in each group.

    Returns
    -------
    dict
        Updated dictionary with same keys as the input `Data`, but with modified
        datasets from this function.

    """
    print("Start of tidy_param()")       
    
    vdict = Data.copy()
    
    #%% Join procedure
    
    if Join == True:
        # Check if input arguements are valid
        join = Join 
                
        ## Check Join_file type
        if type(Join_file).__name__ != "str":
            wmsg = "Warning: `Join_file` is not of type `str`. Skipping Join procedure."
            warnings.warn(wmsg)
            join = False
    
        # Check Join_file existance            
        if not os.path.exists(Join_file):        
            wmsg = "Warning: `Join_file` does not exist at specified path. Skipping Join procedure."
            warnings.warn(wmsg)
            join = False
            
        # Check Join_file_form type
        if type(Join_file_form).__name__ != "str":
            wmsg = "Warning: `Join_file_form` is not of type `str`. Skipping Join procedure."
            warnings.warn(wmsg)
            join = False
            
        # Check Join_file_form validity
        if Join_file_form.casefold() not in ['csv', 'tsv']:
            wmsg = f"Warning: {Join_file_form} is not a valid `Join_file_form`. Skipping Join procedure."
            warnings.warn(wmsg)
            join = False
                
        # Run the Join procedure 
        if join == True:
            
            # Load the external join dataset
            if Join_file_form.casefold() == "csv":
                Join_Data2 =  pd.read_csv(Join_file)
            else:
                Join_Data2 = pd.read_csv(Join_file, delim_whitespace=False)     
            
            # Join external dataset to each item in variable dictionary
            for var in vdict.keys():
                try:
                    vdict[var] = tidy.join_data(Data1=vdict[var], Data2=Join_Data2, Group=Join_grp)
                except:
                    wmsg = f"Warning: Join procedure failed unexpectedly for variable {var}. Returning original dataset."
                    warnings.warn(wmsg)
                    pass
        
    #%% Aggregation procedure
    
    # Specify temporal and spatial variables that should not be aggregated
    ## Time_spat = non data columns (not the target for aggregation, rollmean, ... etc)
    ## TODO: Automate time_spat so it will grab any col where the last two characters are 'id' as well as the time 
    time_spat = ['date', 'dec', 'year', 'month', 'day'] # time scale
    time_spat = time_spat + ['sdec', 'syr', 'smth', 'sday'] # simulation time scale
    time_spat = time_spat + ['basinid', 'hillslopeid', 'hillid', 'zoneid', 'patchid', 'stratumid', 'strataid', 'vegid','id', 'veg_parm_id'] # temporal scale
                                  
    if Agg == True:
        for var in vdict.keys():                        
            vlist = [item for item in vdict[var].columns if item.casefold() not in time_spat] # list of variables to aggregate
            try:
                vdict[var] = tidy.agg(Dataframe=vdict[var], 
                                             Varlist=vlist, 
                                             Group1=Agg_grp1, 
                                             Group2=Agg_grp2, 
                                             Method=Agg_method
                                             )
            except:
                wmsg = f"Warning: Aggregation procedure failed unexpectedly for variable {var}. Returning original dataset."
                warnings.warn(wmsg)
                pass
    
    #%% Rolling mean procedure
    
    if Rollmean == True:
        for var in vdict.keys():
            vlist = [item for item in vdict[var].columns if item.casefold() not in time_spat] # list of variables to aggregate            
            
            try:
                vdict[var] = tidy.rollmean(vdict[var], Varlist=vlist, K=Rollmean_k, Group=Rollmean_grp)
            except:
                wmsg = f"Warning: Rollmean procedure failed unexpectedly for variable {var}. Returning original dataset."
                warnings.warn(wmsg)
                pass
    
    #%% End of tidy module
    print("End of tidy_param()", '\n'*2)
    return vdict                    

#%% Call the main function if this is the main script
if __name__ == '__main__':
    print("Start of tidy_param()")
    tidy_param()
    print("End of tidy_param()")