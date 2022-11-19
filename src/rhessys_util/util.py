# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:53:17 2022

@author: jonge
"""
#%% Import required modules
import os
import sys
import numpy as np
import pandas as pd
import warnings

#%% Function to read input settings file

def import_settings(File: str, TSV: bool = False) -> dict:
    """
    Extracts program settings from either a TSV or CSV file and saves to dictionary

    Parameters
    ----------
    File : str
        File with program settings to extract.
        
    Format : str
        Format of `File`. Either tab separted (white space) or comma separated.
        Default is tab separated

    Returns
    -------
    None.

    """
          
    # Check if function parameters are valid
    if type(File).__name__ != 'str':
        print("Error: `File` is not a string.")
        return None 
    
    t1 = os.path.exists(File)
    if not t1:
        print("Error: `File` does not exists.")
        return None
    
    if type(TSV).__name__ != 'bool':
        print("Error: `TSV` is not a bool.")
        return None
    
    # Read file in as table
    if TSV == True:
        # tab-separted file
        df = pd.read_csv(File, delim_whitespace=True, comment="#")
    else:
        # comma-separated file
        df = pd.read_csv(File, delim_whitespace=False, comment="#")
    
    prog_set = dict()

    for var, func, typ, val in df[['variable','function', 'type', 'value']].values:
        # Remove parenthesis from row values and convert to strings (or list)
        var2 = var.replace('\"', '').replace(' ', '').split(',')[0]        
        func2 = func.replace('\"', '').replace(' ', '').split(',')[0]
        typ2 = typ.replace('\"', '').replace(' ', '').split(',')[0]
        
        val2 = val.replace('\"', '').replace(' ', '').split(',')        
        
        if typ2.casefold() != 'list':
            val2 = ' '.join(val2)
            if val2.casefold() == 'none':
                val2 = None
            elif val2.casefold() == "true":
                val2 = True
            elif val2.casefold() == 'false':
                val2 = False
            
            if typ2.casefold() == "int":
                try:
                    val2 = int(val2)
                except:
                    wmsg = f"Warning: {val2} could not be coerced to `int`. Keeping as `str`."
                    warnings.warn(wmsg)
                    pass
            
        else:            
            ltmp = []
            for item in val2:
                if item.casefold() == 'none':
                    ltmp.append(None)
                elif item.casefold() == "true":
                    ltmp.append(True)
                elif item.casefold() == "false":
                    ltmp.append(False)
                else:
                    ltmp.append(item)
            val2 = ltmp                            
                        
        #if typ2.casefold() == 'bool':
        #    val2 = [val2.casefold() == 'true'][0]            
            
        # save variable, function, class, and value to the dictionary
        prog_set[var2] = {
            "function" : func2,
            "class" : typ2,
            "value" : val2
            }
        
    return prog_set

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
        return None 
    
    if type(Delim).__name__ != 'str':
        print("Error: `Delim` is not a string.")
        return None
    
    if type(ID_loc).__name__ != 'list':
        print("Error: `ID_loc` is not a list.")
        return None
    
    if type(inc_patn).__name__ != 'list':
        print("Error: `inc_patn` is not a list.")
        return None
    
    if type(ex_patn).__name__ != 'list':
        print("Error: `ex_patn` is not a list.")
        return None
    
    # Check if the specified directory path exists
    if not os.path.exists(Path):
        print("Error: 'Path' is invalid.")
        return None
    
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
    
    dir_exclude = ['storage', 'defs', 'param', 'archive', 'awk', 'util']
    
    for root, dirs, files in os.walk(tarpath, topdown=True):
        dirs[:] = [d for d in dirs if d not in dir_exclude]
        for file in files:
            # Filter by `inc_patn` and `ex_patn`
            if None not in inc_patn and None not in ex_patn:
                lt = bool(all([ptn in file for ptn in inc_patn]) * all([ptn not in file for ptn in ex_patn]))                                                        
            elif None not in inc_patn:
                lt = bool(all([ptn in file for ptn in inc_patn]))                                                        
            else:
                print("Error: No inc_patn or ex_patn specified")
                return None
                                
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
    colnames=['i'+str(i) for i in range(0,ncol)] # name each column as i<int>
        
    # Create the filelist dataframe using the idlist array as a skeleton
    df0 = pd.DataFrame(idlist, columns=colnames)    
    
    # Add the files to the filelist dataframe
    try:
        df0['file'] = filelist        
    except:
        df0['file'] = np.nan
    
    # Sort the dataframe by the colnames identifier (typically these are integers in increasing order)
    df0.sort_values(by=colnames)
    
    return df0

#%% Count number of none blank lines in a file
def count_line(File: str) -> int:
    """
    Counts the number of none blank lines in a file. Intended for csv or tsv format
    files.

    Parameters
    ----------
    File : str
        Path to the file to be read.

    Returns
    -------
    int
        Total number of lines in file that contain more than just whitespace.

    """
    
    count = 0
    with open(File) as fp:
        for line in fp:
            if line.strip():
                count += 1
    return count
