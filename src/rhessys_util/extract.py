# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:45:21 2022

@author: jonge
"""

#%% Imports
import os
import numpy as np
import pandas as pd

#%% Create a filelist
def filelist(Path: str, Delim: str, ID_loc: list, inc_patn: list, ex_patn: list) -> pd.DataFrame:
    """
    Searches all files contained in subdirectories of `Path` to find only those that
    contain all patterns specified in `inc_patn` and do not contain all patterns
    specified in `ex_patn`. For each file found, keeps a running list of the the
    following:\n
    (1) Filename (fullpath)\n
    (2) File identifiers specified by `Delim` and `ID_loc`.
    
    These running lists are then combined into a 2-dimensional Pandas Dataframe,
    and rows are sorted by alpha-numerical order (based on `ID_loc` as columns).

    Parameters
    ----------
    Path : str
        Path to top of directory tree that will be searched for files.
        
    Delim : str
        Deliminator used to split the filename and extract file identifiers (i.e. "_").
        
    ID_loc : list
        Index position of identifiers to extact from each file; each file is split into
        a list of strings (each string is separated by `Delim`), and then list values
        specified by `ID_loc` are extracted from this list. If the string produced by this
        split process has fewer elements than those specified by `ID_loc`, then nan is used
        for both file identifiers of that file.
        
    inc_patn : list
        List of patterns (strings) used restrict files added to the filelist; all filenames
        that contain `inc_patn` will potentially be added to the running filelist, so long
        as they also do not contain all patterns found in `ex_patn`.
        
    ex_patn : list
        List of patterns (strings) used restrict files added to the filelist; all filenames
        that do not contain 'ex_patn` will potentially be added to the running filelist, so long
        as they also contain all patterns found in `inc_patn`.

    Returns
    -------
    pd.DataFrame
        Dataframe containing filenames and associated file identifiers as columns.
        
    """
    
    # First check if all arguements are correct (type, and size)
    if type(Path).__name__ != 'str':
        print("Error: `Path` is not a string.")
        return 0 
    
    if type(Delim).__name__ != 'str':
        print("Error: `Delim` is not a string.")
        return 0
    
    if type(ID_loc).__name__ != 'list':
        print("Error: `ID_loc` is not a list.")
        return 0
    
    if type(inc_patn).__name__ != 'list':
        print("Error: `inc_patn` is not a list.")
        return 0
    
    if type(ex_patn).__name__ != 'list':
        print("Error: `ex_patn` is not a list.")
        return 0
    
    # Check if the specified directory path exists
    if not os.path.exists(Path):
        print("Error: 'Path' is invalid.")
        return 0
    
    # Normalize the target directory path
    tarpath = os.path.normpath(Path)
        
    # Create empty arrays for roots, files, and tags
    rootlist = np.empty(0)
    filelist = np.empty(0)
    idlist = np.empty(0)
    
    # Using os.walk(), create a file structure tree object, and then loop through
    # all the files to create a filelist whilst also extracting specified file 
    # identitiers (ID_loc). Only keep files that contain `inc_patn` and do not 
    # contain `ex_patn`
    
    for root, dirs, files in os.walk(tarpath):
        for file in files:
            # Filter by `inc_patn` and `ex_patn`
            lt = bool(all([ptn in file for ptn in inc_patn]) * all([ptn not in file for ptn in ex_patn]))                                                        
            # If file exists, add root, filename, and ids to their lists
            if lt:
                rootlist = np.append(rootlist, np.array(root))
                filelist = np.append(filelist, os.path.join(root, file))
                if len(ID_loc) > 0:
                    try:
                        idtmp = np.array(file.split(Delim))[ID_loc]                    
                    except:
                        idtmp = np.empty(len(ID_loc))
                        idtmp[:] = np.nan
                
                    idlist = np.append(idlist, idtmp)
                else:
                    idtmp = np.empty(1)
                    idtmp[:] = np.nan
                    idlist = np.append(idlist, idtmp)
            
 
    
    # Reshape the idlist to a 2d array with #cols = length of ID_loc list
    if len(ID_loc) < 1:
        ncol = 1
    else:
        ncol = len(ID_loc)
        
    idlist = idlist.reshape((int(len(idlist)/ncol), ncol))
    colnames=['i'+str(i) for i in range(0,ncol)]
    
    # Create the filelist dataframe using the idlist array as a skeleton
    df0 = pd.DataFrame(idlist, columns=colnames)    
    
    # Add the files to the filelist dataframe
    try:
        df0['file'] = filelist        
    except:
        df0['file'] = np.nan
    
    # Sort the dataframe by the colnames identifier (typically these are integers)
    df0.sort_values(by=colnames)
    
    return df0


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

def rhessys(File: str, Spat: str, Time: str, Varlist: list, Bounds: list = [None,None]) -> pd.DataFrame:
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
        checklist += ['year', 'month', 'day']
    elif Time == "monthly":
        checklist += ['year', 'month']
    elif Time == "yearly":
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
    checklist = np.array(checklist)
    checklist_lwr = np.core.defchararray.lower(checklist)
    hdr_lwr = np.core.defchararray.lower(hdr)
    
    #ltest = np.array([item in hdr for item in checklist])
    ltest = np.array([item in hdr_lwr for item in checklist_lwr])
    
    if not all(ltest):
        print('Error: The following requested variable(s) are not valid:\n{}'
              .format(checklist[~ltest]))
        return None
    
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
        st = Bounds[0]
        
    if Bounds[1] == None:
        end = None
    else:
        end = Bounds[1] - Bounds[0] + 1
    
    # 4th load in the variables
    # -> create an if condition or a switch that makes decisions based on `Spat` and `Time`
    # -> this will determine what variables to load in addion to variables requested by `Varlist`
    # -> make sure the list is case insenstive
    
    try:
        df = pd.read_csv(File,
                         skipinitialspace=True,
                         delim_whitespace=True,
                         #usecols=checklist
                         usecols= lambda x: x.lower() in checklist_lwr,
                         skiprows=st,
                         nrows=end
                         )
        print("Successfully loaded file:\n{}".format(File))
        return df
    
    except:
        print("Unsuccessfully loaded file:\n{}".format(File))
        return None