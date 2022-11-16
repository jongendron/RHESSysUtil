# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:45:21 2022
*rhessys() is not designed as a standalone function, so source entire file.*

@author: jonge
"""

#%% Imports
import os
import numpy as np
import pandas as pd

#%% Read header names of a RHESSys output file
def header(File: str) -> list:
    """
    Reads a RHESSys output file (`File`) in csv or tabular format, and returns 
    the column headers as a list.

    Parameters
    ----------
    File : str
        RHESSys output file to parse.

    Returns
    -------
    list
        List of header names from `File`.

    """
    
    with open(File, "r") as ofile:
        hdr = ofile.readline().split()
    return hdr

#%% Load in RHESSys output file based on spatial scale, temporal scale, and variable list

def rhessys(File: str, Spat: str, Time: str, Varlist: list, Bounds: list = [None,None], Simtime: bool = True) -> pd.DataFrame:
    """
    Reads a RHESSys output file (`File`) creates a pandas DataFrame object based 
    on the spatial scale (`Spat`), the time scale (`Time`), and a variable list 
    (`Varlist`). 

    Parameters
    ----------
    File : str
        RHESSys output file to be read.
        
    Spat : str
        Spatial scale of RHESSys output file (basin, hillslope, zone, patch, stratum).
        
    Time : str
        Time scale of RHESSys output file (daily, monthly, yearly).
        
    Varlist : list
        List of variables to be extracted from `File`.
        
    Bounds : list
        List of the start and end rows to be read from the input file [Start, End]. Indexes start
        with 0, (i.e) [None,2] extracts the first 3 rows of the file (after the header).
        If Start = None, reads from first line; if End = None, reads all lines after start.
        
    Simtime : bool
        Boolean switch used to determine if the program should check for available 
        simulation time variables ('sday', 'smth', 'syr') and extract them.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with variables in wide format (column-wise); variabels are
        based on `Varlist`, as well as the `Spat` and `Time` flags.

    """
    
    # 1st check if Spatial and Temporal scales requested are valid options
    if Spat not in ['basin', 'hillslope', 'zone', 'patch', 'stratum', 'custom']:
        print("Error: Spatial scale, {}, is not a valid option".format(Spat))
        return None
    
    if Time not in ['daily', 'monthly', 'yearly', 'custom']:
        print("Error: Temporal scale, {}, is not a valid option".format(Time))
        return None
    
    # 2nd check if requested variables from `Spat`, `Time`, and `Vlist` are available
    hdr = np.array(header(File = File))    
    checklist = Varlist.copy()     
    
# =============================================================================
#     # Check which simtime terms are available to extract and add to checklist
#     if Simtime == True:
#         simtime_cols = [stime for stime in hdr if stime.casefold() in ["sday", "smth", "syr"]]
#         if len(simtime_cols) > 0:
#             checklist += simtime_cols
# =============================================================================
    
    # Extract necessary spatial variables based on spatial timescale
    if Spat == "basin":
        checklist += ['basinID']
    elif Spat == "hillslope":
        checklist += ['hillslopeID']
    elif Spat == "zone":
        checklist += ['zoneID']
    elif Spat == "patch":
        checklist += ['patchID']
    elif Spat == "stratum":
        checklist += ['patchID', 'stratumID']
    elif Spat == "custom":        
        while True:            
            vtmp = input("Enter a variable associated with Spat or pass `0` or `exit` finish\n->")
            if vtmp == '0' or vtmp == 'exit':
                break
            checklist += [vtmp]
            print('Added {} to checklist. Current checklist includes:\n{}'
                  .format(vtmp, checklist))
    
    # Extract necessary time variables based on temporal timescale
    if Time == "daily":
        if Simtime == True:
            checklist += ["sday", "smth", "syr"] # add simtime terms
        checklist += ['year', 'month', 'day']
    elif Time == "monthly":
        if Simtime == True:
            checklist += ["smth", "syr"] # add simtime terms
        checklist += ['year', 'month']
    elif Time == "yearly":
        if Simtime == True:
            checklist += ["syr"] # add simtime terms
        checklist += ['year']
    elif Time == "custom":
        while True:            
            vtmp = input("Enter a variable associated with Time or pass `0` or `exit` to finish\n->")
            if vtmp == '0' or vtmp == 'exit':
                break
            checklist += [vtmp]
            print('Added {} to checklist. Current checklist includes:\n{}'
                  .format(vtmp, checklist))
    else:
        print("Error: `Time` arguement provided is invalid.")
        return None
    
    # Now compare checklist to hdr to see if all variables are available
    # checklist = np.array(checklist)
    # checklist_lwr = np.core.defchararray.lower(checklist)
    # hdr_lwr = np.core.defchararray.lower(hdr)
    
    #ltest = np.array([item in hdr for item in checklist])
    # ltest = np.array([item in hdr_lwr for item in checklist_lwr])
    foundlist = [col for col in hdr if col.casefold() in [col2.casefold() for col2 in checklist]]    
    
    # if not all(ltest):
    #    print('Error: The following requested variable(s) are not valid:\n{}'
    #          .format(checklist[~ltest]))
    #    return None
    
    # Check if all requested variables where found
    if len(foundlist) != len(checklist):
        elist = [col.casefold() for col in checklist if col not in [col2.casefold() for col2 in hdr]]         
        print('Error: The following requested variable(s) are not valid:\n{}'.format(elist))
    
    # 3rd Check if bounds are valid and make correction
    if type(Bounds).__name__ != 'list':
        print("Error: `Bounds` is not a list.")
        return None
    
    if len(Bounds) < 1:
        print("Error: Must be two bounds.")
        return None
    
    if Bounds[0] == None:
        st = 0
    else:
        st = int(Bounds[0])
        
    if Bounds[1] == None:
        end = None
    else:
        end = int(Bounds[1]) - st + 1
    
    # 4th load in the variables
    # -> create an if condition or a switch that makes decisions based on `Spat` and `Time`
    # -> this will determine what variables to load in addion to variables requested by `Varlist`
    # -> make sure the list is case insenstive
    
    try:
        df = pd.read_csv(File,
                         skipinitialspace=True,
                         delim_whitespace=True,
                         usecols=foundlist,
                         #usecols= lambda x: x.lower() in checklist_lwr,
                         skiprows=st,
                         nrows=end
                         )
        print("Successfully loaded file:\n{}".format(File))
        return df
    
    except:
        print("Unsuccessfully loaded file:\n{}".format(File))
        return None
    
# =============================================================================
# #%% Function to Extract Variable Output From a list of files and merge into wide dataframe
# #def merge_sims(Filelist: list, Varlist: list, Spat: str, Time: str, Bounds: list = [None, None], Random: bool = False) -> list:
# def merge_sims(Filelist: list, Varlist: list, Spat: str, Time: str, Bounds: list = [None, None], Check_date: bool = False) -> list:
#     """
#     Function to extract specified columns of data from a multiple files (csv or tsv)
#     and then merge them into a list of dataframes. For each variable in `Varlist`
#     a dataframe is assigned as a list element, wherein the number of columns is equal
#     to the file length + the number of spatial and temporal identifies are associated
#     with the filetype; spatial and temporal identifies are governed by 'Spat' and 'Time'
#     according to the functions_postprocessing_1.read_rhessys() function. 
#     
#     Parameters
#     ----------
#     Filelist : list
#         List of files to extract dataframe. These are to be RHESSys output files in 
#         csv or tsv format.
#     Varlist : list
#         List of variables to extract from each file in `Filelist`. These variables
#         must exist as columns in each file in `Filelist` to load the data.
#     Bounds : list
#         List of the starting and ending row number to load from each file in `Filelist`.
#         Indexes start from 0, and by default the header of each file is not counted as a row.
#     Spat : str
#         Spatial scale of the input files in `Filelist`. See read_rhessys() for more info.
#     Time : str
#         Temporal scale of the input files in `Filelist`. See read_rhessys() for more info.
#     Check_date : bool, optional
#         If `True`, include date identifies in the comparison of columns extracted 
#         from each file in `Filelist` and the initialized pd.DateFrame built for each variable.
#         If `False`, Do not include date identifies ('day', 'month', 'year') in the comparison.
#         The default is False.
# 
#     Returns
#     -------
#     dict
#         Returns a dict of `n` dataframes, were `n` is equal to the length of `Varlist`.
#         For each key/dataframe, the number of columns is equal to the file list length + 
#         the number of spatial and temporal identifies associated with with the filetype.
# 
#     """        
#     # Declare length variables and empty variable dictionary
#     nvar = len(Varlist)   # number of variables
#     nfile = len(Filelist) # number of files
#     # datlist = list()
#     vdict = {} # empty dictionary
#     
#     # Initialize Create empty list with as many empty sublist as there variables
#     for i in range(0,nvar):
#         # datlist.insert(i, [])
#         vdict[Varlist[i]] = None # empty value for dictionary key
#     
#     for i in range(0,nfile):        
#         # Read in the RHESSys file with target variables
#         # Make sure that this step only reads spatial/time variables + target varaibles (may need to change rhessys to include simtime switch) ############## TODO:
#         dat = rhessys(File=Filelist[i], Spat=Spat, Time=Time, Varlist=Varlist, Bounds=Bounds)
#         if type(dat).__name__ == 'NoneType':
#             continue
#         
#         # Obtain list of column names that are not in `Varlist`
#         #tid = [col not in Varlist for col in dat.columns] # find column not specified as taget variables
#         #tcol = dat.columns[tid].tolist()                  # create a list of these
#         tcol = [col for col in [dcol.casefold() for dcol in dat.columns] if col not in [ccol.casefold() for ccol in Varlist]] # All vars not in Varlist (but casefold)                    
#         
#         # Obtain list of column to compare against initialized dataFrame values during dataFrame merging        
#         if Check_date == False:
#             # Remove all time variables that are not simtime from tcol
#             #ltcol = [item if item.casefold() not in ['day', 'month', 'year'] for item in tcol] # columns to compare with inititalized dataframe        
#             #[item for item in ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE'] if item.casefold() not in ['one', 'two', 'three']] # list constructor
#             ltcol = [item for item in tcol if item.casefold() not in ['day', 'month', 'year']]
#         else:
#             # Keep all variables in tcol
#             ltcol = tcol.copy()
#                                     
#         # Loop through varlist and extract series of each variable -> nested dictionary
#         for j in range(0,nvar):
#             # Check if the dataframe has been initialized for each variable                                                
#             if vdict[Varlist[j]] == None: 
#                 # If not initialized, used the current dataFrame (dat) to do so
#                 # Initialize the data frame
#                 # datlist[j] = dat[tcol].copy()
#                 # datlist[j][str(i+1)] = dat[Varlist[j]].copy()
#                 vdict[Varlist[j]] = dat[tcol].copy() # shallow copy, no nested list
#                 vdict[Varlist[j]][str(i+1)] = dat[Varlist[j]].copy() # same                                                
#             else:                
#                 # If initialized, compares all column series in ltcol with series in vdict                
#                 #TODO: find a way to ensure all columns from dat that are in ltcol are in vdict
#                                 
#                 keep = True
#                 for z in range(0,len(ltcol)):                                        
#                     # 1st check for same number of rows
#                     # if len(datlist[j][ltcol[z]].values) != len(dat[ltcol[z]].values):
#                     if len(vdict[Varlist[j]][ltcol[z]].values) != len(dat[ltcol[z]].values):
#                         print("Error: Incompatable number of rows in loaded file.")
#                         keep = False
#                     if not all(vdict[Varlist[j]][ltcol[z]].values == dat[ltcol[z]].values):
#                         print("Error: Incompatable number of rows in loaded file.")
#                         keep = False                                                                         
#                      
#                     # Check for same values if temporal data is not randomized
#                     # if Random == False and not all(datlist[j][ltcol[z]].values == dat[ltcol[z]].values):
#                         # print("Error: Incompatable number of rows in loaded file.")
#                         # keep = False
#                         
#                 if keep == True:
#                     # datlist[j][str(i+1)] = dat[Varlist[j]].copy()
#                     vdict[Varlist[j]][str(i+1)] = dat[Varlist[j]].copy()
#                     
#     #return datlist
#     return vdict
# =============================================================================
