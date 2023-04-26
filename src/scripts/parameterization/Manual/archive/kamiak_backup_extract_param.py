# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 18:32:04 2022
extract_param() is not desinged to be a stand-alone function -- 
-- dependencies from rhessys_util

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

from rhessys_util import extract

#%% Define the export_param function
# Requires
def extract_param(Filelist: list, Varlist: list, Spat: str, Time: str, Bounds: list = [None, None], Check_date: bool = False, Simtime: bool = True) -> list:
    """
    Function to extract specified columns of data from a multiple files (csv or tsv)
    and then merge them into a list of dataframes. For each variable in `Varlist`
    a dataframe is assigned as a list element, wherein the number of columns is equal
    to the file length + the number of spatial and temporal identifies are associated
    with the filetype; spatial and temporal identifies are governed by 'Spat' and 'Time'
    according to the functions_postprocessing_1.read_rhessys() function. 
    
    Parameters
    ----------
    Filelist : pd.DataFrame
        Dataframe containing series of files to extract dataframe and accompanying tags
        to identify each simulation; these should be extracted from the RHESSys 
        output filenames during filelist_param() and need to match up
        with the tags found in the associated parameter file for each simulation.    
    Varlist : list
        List of variables to extract from each file in `Filelist`. These variables
        must exist as columns in each file in `Filelist` to load the data.
    Bounds : list
        List of the starting and ending row number to load from each file in `Filelist`.
        Indexes start from 0, and by default the header of each file is not counted as a row.
    Spat : str
        Spatial scale of the input files in `Filelist`. See read_rhessys() for more info.
    Time : str
        Temporal scale of the input files in `Filelist`. See read_rhessys() for more info.
    Check_date : bool, optional
        If `True`, include date identifies in the comparison of columns extracted 
        from each file in `Filelist` and the initialized pd.DateFrame built for each variable.
        If `False`, Do not include date identifies ('day', 'month', 'year') in the comparison.
        The default is False.
    Simtime : bool, optional
        If 'True' include check for and use simtime variables ('sday', 'smth', 'syr') from RHESSys outputfile.
        If 'False' disclude check for these variable. Furthermore, `daily`, `monthly`, and `yearly` time scale
        checks for separate variables. See extract.py for more information.

    Returns
    -------
    dict
        Returns a dict of `n` dataframes, were `n` is equal to the length of `Varlist`.
        For each key/dataframe, the number of columns is equal to the file list length + 
        the number of spatial and temporal identifies associated with with the filetype.

    """        
    print("Start of extract_param()", '\n'*2)
    # Check if function arguements are valid
    if type(Filelist).__name__ != 'DataFrame':
        print("Error: `Filelist` is not a DataFrame.")
        return None     
    
    if type(Varlist).__name__ != 'list':
        print("Error: `Varlist` is not a list.")
        return None 
    
    # Time and spat are already checked in rhessys_util.extract.rhessys()    
    
    # Declare length variables and empty variable dictionary
    nvar = len(Varlist)   # number of variables
    nfile = Filelist.shape[0] # number of files & tags (rows of the DataFrame)    
    vdict = {} # empty dictionary
    
    # Initialize Create empty list with as many empty sublist as there variables
    for i in range(0,nvar):
        # datlist.insert(i, [])
        # vdict[Varlist[i]] = None # empty value for dictionary key
        vdict[Varlist[i]] = pd.DataFrame() # empty pd.DataFrame for dictionary key
    
    for i in range(0,nfile):        
        # Read in the RHESSys file with target variables
        # Make sure that this step only reads spatial/time variables + target varaibles (may need to change rhessys to include simtime switch) ############## TODO:
        dat = extract.rhessys(File=Filelist['file'][i], Spat=Spat, Time=Time, Varlist=Varlist, Bounds=Bounds, Simtime=Simtime) # TODO: Include setting for grabbing simtime
        if type(dat).__name__ == 'NoneType':
            continue
        
        # Obtain list of column names that are not in `Varlist`
        #tid = [col not in Varlist for col in dat.columns] # find column not specified as taget variables
        #tcol = dat.columns[tid].tolist()                  # create a list of these
        tcol = [col for col in [dcol for dcol in dat.columns] if col.casefold() not in [ccol.casefold() for ccol in Varlist]] # All vars not in Varlist (but casefold)                    
        
        # Obtain list of column to compare against initialized dataFrame values during dataFrame merging        
        if Check_date == False:
            # Remove all time variables that are not simtime from tcol
            #ltcol = [item if item.casefold() not in ['day', 'month', 'year'] for item in tcol] # columns to compare with inititalized dataframe        
            #[item for item in ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE'] if item.casefold() not in ['one', 'two', 'three']] # list constructor
            ltcol = [item for item in tcol if item.casefold() not in ['day', 'month', 'year']]
        else:
            # Keep all variables in tcol
            ltcol = tcol.copy()
            
        # Based on time scale, restrict which simtime variables to check for same values
        if Time.casefold() == "daily":
            ltcol = [item for item in ltcol if item.casefold() not in ['smth', 'syr']] # don't check smth or syr for daily
        elif Time.casefold() == "monthly":
            ltcol = [item for item in ltcol if item.casefold() not in ['sday', 'syr']] # don't check sday or syr for monthly
        elif Time.casefold() == "yearly":
            ltcol = [item for item in ltcol if item.casefold() not in ['sday', 'smth']] # don't check sday or smth for yearly
                          
        # Loop through varlist and extract series of each variable -> nested dictionary
        for j in range(0,nvar):
            # Check if the dataframe has been initialized for each variable                                                
            if vdict[Varlist[j]].empty:
                vdict[Varlist[j]] = dat[tcol].copy() # shallow copy, no nested list
                # vdict[Varlist[j]][str(i+1)] = dat[Varlist[j]].copy() # Use if you just want to count iteratively
                vdict[Varlist[j]][Filelist['i1'][i]] = dat[Varlist[j]].copy() # Use if you want to preserve tags extracted from files                              
            else:                
                # If initialized, compares all column series in ltcol with series in vdict                
                #TODO: find a way to ensure all columns from dat that are in ltcol are in vdict
                                
                keep = True
                for z in range(0,len(ltcol)):                                                            
                    # 1st check for same number of rows                
                    if len(vdict[Varlist[j]][ltcol[z]].values) != len(dat[ltcol[z]].values): 
                        # If the working dictionary has more rows
                        if len(vdict[Varlist[j]][ltcol[z]].values) > len(dat[ltcol[z]].values):
                            # Compare data up-to length of shorter dataframe
                            if not all(vdict[Varlist[j]].iloc[0:(len(dat[ltcol[z]].values + 1)),:][ltcol[z]].values == dat[ltcol[z]].values):
                                print(f"Error: Values in column {ltcol[z]} do not match.")
                                keep = False
                            # If they match, then reduce size of larger dataframe
                            else:
                                print(f"Values in column {ltcol[z]} match up to row {dat.shape[0] + 1}. Keepings only these cols.")
                                vdict[Varlist[j]] = vdict[Varlist[j]].iloc[0:(len(dat[ltcol[z]].values + 1)),:]
                        # If working dictionary has fewer rows
                        else:
                            # Compare data up-to length of shorter dataframe
                            if not all(vdict[Varlist[j]][ltcol[z]].values == dat.iloc[0:(len(vdict[Varlist[j]][ltcol[z]].values) + 1),:][ltcol[z]].values):
                                print(f"Error: Values in column {ltcol[z]} do not match.")
                                keep = False
                            # If they match, then reduce size of larger dataframe
                            else:
                                print(f"Values in column {ltcol[z]} match up to row {vdict[Varlist[j]].shape[0] + 1}. Keepings only these cols.")
                                dat = dat.iloc[0:(len(vdict[Varlist[j]][ltcol[z]].values) + 1),:]                                
                                                            
                                                
                    elif not all(vdict[Varlist[j]][ltcol[z]].values == dat[ltcol[z]].values):
                        print(f"Error: Values in column {ltcol[z]} do not match.")
                        keep = False                                                                        
                
                if keep == True:                    
                    # vdict[Varlist[j]][str(i+1)] = dat[Varlist[j]].copy() # Use if you want to preserve tags extracted from files                              
                    vdict[Varlist[j]][Filelist['i1'][i]] = dat[Varlist[j]].copy() # Use if you want to preserve tags extracted from files                              
                        
    print("End of extract_param()", '\n'*2)
    return vdict
            
#%% Call the main function if this is the main script
if __name__ == '__main__':
    print("Start of extract_param()", '\n')
    extract_param()
    print("End of extract_param()", '\n')

