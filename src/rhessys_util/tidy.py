# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:27:55 2022

@author: jonge
"""
import numpy as np
import pandas as pd
from .extract import rhessys

#%% Function to Extract Variable Output From a list of files and merge into wide dataframe
def merge_sims(Filelist: list, Varlist: list, Spat: str, Time: str, Bounds: list = [None, None], Random: bool = False) -> list:
    """
    Function to extract specified columns of data from a multiple files (csv or tsv)
    and then merge them into a list of dataframes. For each variable in `Varlist`
    a dataframe is assigned as a list element, wherein the number of columns is equal
    to the file length + the number of spatial and temporal identifies are associated
    with the filetype; spatial and temporal identifies are governed by 'Spat' and 'Time'
    according to the functions_postprocessing_1.read_rhessys() function. 
    
    Parameters
    ----------
    Filelist : list
        List of files to extract dataframe. These are to be RHESSys output files in 
        csv or tsv format.
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
    Random : bool, optional
        If `True`, compares only the number of rows extracted from each file in `Filelist`.
        If `False`, compares both the number of rows and the value of spatial and temporal
        identifiers to ensure a match between each file in `Filelist`. The default is False.

    Returns
    -------
    list
        Returns a list of `n` dataframes, were `n` is equal to the length of `Varlist`.
        For each dataframe, there the number of columns is equal
        to the file length + the number of spatial and temporal identifies are associated
        with the filetype.

    """        
    nvar = len(Varlist)   # number of variables
    nfile = len(Filelist) # number of files
    datlist = list()
    
    # Create empty list with as many empty sublist as there variables
    for i in range(0,nvar):
        datlist.insert(i, [])
    
    for i in range(0,nfile):        
        # Read in the RHESSys file with target variables
        dat = rhessys(File=Filelist[i], Spat=Spat, Time=Time, Varlist=Varlist, Bounds=Bounds)
        if type(dat).__name__ == 'NoneType':
            continue
        
        # Obtain list of column names that are not in `Varlist`
        tid = [col not in Varlist for col in dat.columns] # find column not specified as taget variables
        tcol = dat.columns[tid].tolist()                  # create a list of these
                
        for j in range(0,nvar):    
            if not list(datlist[j]):
                # Initialize data frame            
                #datlist.insert(j, dat[tcol].copy())
                datlist[j] = dat[tcol].copy()
                datlist[j][str(i+1)] = dat[Varlist[j]].copy()                        
            else:
                # 1st check if None variabels match
                keep = True
                for z in range(0,len(tcol)):                    
                    
                    # Check for same number of rows
                    if len(datlist[j][tcol[z]].values) != len(dat[tcol[z]].values):
                        print("Error: Incompatable number of rows in loaded file.")
                        keep = False
                    
                    # Check for same values if temporal data is not randomized
                    if Random == False and not all(datlist[j][tcol[z]].values == dat[tcol[z]].values):
                        print("Error: Incompatable number of rows in loaded file.")
                        keep = False
                
                if keep == True:
                    datlist[j][str(i+1)] = dat[Varlist[j]].copy()
                    
    return datlist

#%% Create Group index number for all groups in a dataframe (unstable)
def grpidx(Dataframe: pd.DataFrame, Groups: list, ID: str = "GroupID") -> pd.DataFrame:
    """
    Using group keys provided in `Groups`, groups a presorted `Dataframe` and adds
    a column containing the group number associated with each row of data.
    
    Group numbers are given in the order in which they appear, not alphanumerically.
    
    Subsets the `DataFrame` to only contain columns specified by `Groups`, and then
    searches for duplicate rows to assign as groups.
    
    *Function does not handle unsorted pd.DataFrames, with duplicate rows that are 
    out of order, therefore if a row is a duplicate of a prevous group it takes on the value
    of the group just before it and so do all the following rows if they are also duplicates*
    
    *The fault is in just merely searching for unique row combinations, rather in the future,
    this function should sort the data so that it ...
        (1) finds all duplicates
        (2) puts all duplicates after their correct parent
        (3) then assigns groups

    Parameters
    ----------
    Dataframe : pd.DataFrame
        Pandas dataframe to assign group names to.
        
    Groups : list
        List of valid column names that exist in `Dataframe`
        
    ID : str
        String containing the name of the column that will contain group numbers.

    Returns
    -------
    pd.DataFrame
        Modifed version of `Dataframe` that contains a new column expressing group numbers.

    """
    
    # Check if input arguments are valid
    
    hdr = Dataframe.columns
    
    if type(Groups).__name__ != 'list':
        print("Error: `Groups` is not a list.")
        return
    
    if len(Groups) < 1:
        print("Error: Must group by at least one valid column.")
        return
        
    ltest = [item in hdr for item in Groups]
    if not all(ltest):
        print("Error: `Group` choice, {} is not valid."
              .format(np.array(Groups)[ltest]))
        return    
    
    if type(ID).__name__ != 'str':
        print("Error: `ID` is not a string.")
        return
    
    if len(ID) < 1:
        print("Error: `ID` must be at least one character long")
        return
    
    # Create the index array
    nr = Dataframe.shape[0]
    aend = np.array([nr - 1])
    idx_st = Dataframe[Groups].drop_duplicates().index.values[:, np.newaxis]
    idx_end = np.append(idx_st[1:] - 1,aend)[:, np.newaxis]
    idx_rng = np.hstack((idx_st, idx_end))
    idx_grp = (np.arange(0,idx_rng.shape[0]) + 1)[:,np.newaxis]
    idx = np.hstack((idx_grp, idx_rng))

    # Apply the index array to the Dataframe
    df = Dataframe.copy()
    df[ID] = 0
    nr = idx.shape[0]

    # Apply index array function
    for i in range(0,nr):    
        ridx = np.arange(idx[i,1],idx[i,2]+1) # rows to add group id to
        df.iloc[ridx, -1] = idx[i,0] # for all rows in this group label their group number
        
    return df

#%% Add simulation time
def simtime(Dataframe: pd.DataFrame, Time: str, Random: bool) -> pd.DataFrame:
    """
    Currently a beta release of aggregation
    
    Calculation of smth and beyond is not correct ...
    because estimation of smth is not correct ...
    may need to leverage month column to calculate it
    otherwise how do I estimate month based on simulation days?
    
    
    Based on the temporal scale `Time`, formats `Dataframe` to include simulation
    time variables (sday, smth, syr, sdec). `Time` = "custom" lets you select
    any combination of these that are copatable to the input Dataframe.

    Parameters
    ----------
    Dataframe : pd.DataFrame
        RHESSys output data loaded into Python as a pandas dataframe.
        Use read_rhessys() in this library for more stable results.
        
    Time : str        
        Temporal time scale associated with `Dataframe`. This flag notes what 
        variables should be available in `Dataframe` as well as which simulation
        time variables to create. 
        
            Valid options: ('daily', 'monthly', 'yearly', 'custom').
    
    Random : bool
        When True, RHESSys output data used random climate, and therefore the
        lowest time scale must be manually calculated by dividing by the duration
        of this scale, rounding down, and then adding (+1)
        
    Returns
    -------
    pd.DataFrame
        Reformated `Dataframe` object that includes additional simulation time variables

    """
    # Based on specified time scale, check that the table has the correct time columns
    # if basin yearly, check if year exists
    if Time not in ['daily', 'monthly', 'yearly', 'custom']:
        print("Error: Temporal scale, {}, is not a valid option.".format(Time))
        return
    
    if Random not in [True, False]:
        print("Error: Invalid selection for `Random` flag.")
        return

    # Based on `Time` calculate simulation time variabels
    # Note when syr is calculated from daily RHESSys output (sday), simulation
    # years are relative to the start date as an origin
    # whereas when syr is calculated from yearly RHESSys output, simulations years
    # are just counted from the years provided as input
    
    df = Dataframe.copy()
        
    # Determine which simulation variables to calculate and how
    # hier_scale = np.array(['daily', 'monthly', 'yearly', 'decadal'])    
    ## hier_mname = np.array(['day', 'month', 'year', 'decade'])    
    hier_mname = np.array(['day', 'year', 'decade', 'month'])    
    ## hier_sname = np.array(['sday', 'smth', 'syr', 'sdec']) # units per higher hierarchy level    
    hier_sname = np.array(['sday', 'syr', 'sdec', 'smth']) # units per higher hierarchy level    
    # hier_units = np.array([365.25, 12, 10, 10])
    hier_units = np.array([365.25, 10, None, None])
    hier_method = np.array([None, None, None, None]) # None, 0 = independent, 1 = dependent
    
    if Time == 'daily': # (new) sday -> syr -> sdec -> smth (old) sday -> smth -> syr -> sdec 
        #hier_method[:] = [0, 1, 1, 1]
        hier_method[:] = [0, 1, 1, 3]
    elif Time == 'monthly':
        #hier_method[:] = [None, 0, 1, 1]
        hier_method[:] = [None, 2, 1, 0]
    elif Time == 'yearly':
        hier_method[:] = [None, 0, 1, None]
        
    # If climate sequence was not randomly generate, arrange by all available
    # colnames
    
    if Random != True:
        # First find available columns that match requested temporal scale variables            
        hdr = np.array(df.columns)
        hdr_lwr = [item.lower() for item in hdr]            
        ltest = np.array([item in hier_mname for item in hdr_lwr])
        sort_grps = hdr[ltest] # groups for sorting            
        df = df.sort_values(by=list(sort_grps))
        
    # Add simulation time columns to dataframe
    
    for i in range(0,len(hier_method)):
        if hier_method[i] == None:
            continue
        
        elif hier_method[i] == 0:
            df[hier_sname[i]] = np.arange(1,(df.shape[0]+1))
            
        elif hier_method[i] == 1 & (i > 0):
            if hier_method[i - 1] != None:
                df[hier_sname[i]] = np.floor(df[hier_sname[i - 1]]/hier_units[i-1]).astype(int) + 1 # this is the incorrect line
                
            else:
                print("Error: Invalid hier_method object in use, breaking function.")
                return
            
        elif hier_method[i] == 2: # days per year
            df[hier_sname[i]] = np.floor(df[hier_sname[i]]/365.25).astype(int) + 1  
            
        elif hier_method[i] == 3: # group by syr and get index
            df = grpidx(Dataframe=df, Groups=['syr','month'], ID='smth')     # month must be available though
            
        else:
            print("Error: Invalid hier_method object in use, breaking function.")
            return
    
    return df