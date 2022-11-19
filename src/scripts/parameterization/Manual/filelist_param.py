# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 16:04:59 2022

@author: PETBUser
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

from rhessys_util import util # determine which modules required

#%% Define the filelist_param() function
def filelist_param(Path: str, Time: str, Spat: str, Grow: bool, Ptbl: bool = True) -> list:
    
    print("Start of filelist_param()", '\n'*2)
    
    # Check if input arguements are valid        
    if type(Path).__name__ != 'str':
        print("Error: `Path` is not a str.")
        return None
    
    if type(Time).__name__ != 'str':
        print("Error: `Time` is not a str.")
        return None
    
    if type(Spat).__name__ != 'str':
        print("Error: `Spat` is not a str.")
        return None
    
    if type(Grow).__name__ != 'bool':
        print("Error: `Grow` is not a bool.")
        return None
    
    if type(Ptbl).__name__ != 'bool':
        print("Error: `Ptbl` is not a bool.")
        return None

    # Create the inc_patn and ex_patn based on `Time`, `Spatial`, and `Ptbl`    
    if Grow == True:
        inc = "grow_"
        ex = None
    else:
        inc = ""
        ex = "grow"
                    
    if Spat.casefold() in ['basin', 'hillslope', 'zone', 'patch', 'stratum']:                
        inc = "".join([inc, Spat.casefold()])
    else:
        inc = None
        ex = None

    if Time.casefold() in ['daily', 'monthly', 'yearly']:
        inc = ".".join([inc,Time.casefold()])
    else:
        inc = None
        ex = None
    
    # Create dication to store files (and ptbl if requested)
    ftbl = {}
        
    # Create filelist dataFrame of RHESSys output
    # The parameter file number and parameter set number should be the first two
    # tags in the file name (i.e. parfile_parset_...)
    filelist = util.filelist(Path=Path, Delim="_", ID_loc=[0, 1], inc_patn=[inc], ex_patn=[ex])
    
    if filelist.empty:
        print("Error: No RHESSys files found at specified path based on filter arguements.")
        return None
    
    # Add to dictionary
    ftbl['files'] = filelist # could be None
    
    if Ptbl == True:
        # Create parameter list dataFrame to identify each unique simulation
        # these files should end with '_parlist.txt'            
        # parlist = util.filelist(Path=Path, Delim="_", ID_loc=[], inc_patn=["parlist.txt"], ex_patn=[None])
        parlist = util.filelist(Path=Path, Delim="_", ID_loc=[0, 1], inc_patn=["parlist.txt"], ex_patn=[None])
        
        # Check that file tags are the sae        
        if not filelist[['i0','i1']].equals(parlist[['i0','i1']]):
            wmsg = 'Warning: File tag identifiers for RHESSys files and parfiles are not equal.'
            warnings.warn(wmsg)
                            
        if not parlist.empty:            
            parlist = parlist.reset_index(drop=True)
            
            # Create extract parameter values from the parameter and store in a dataframe
            # with the same filename identifiers
            partbl = []
            for file in parlist['file']:
                partbl.append(pd.read_csv(file, delim_whitespace=True)) # files need to be tab deliminated # TODO: Check if this can handle other format
            
            if not partbl:
                print("Error: RHESSys files specified don't exist in this path")
                return None
            partbl = pd.concat(partbl)
            partbl = partbl.reset_index(drop=True)
            
            # Add tags to partable (if tags are not inside of partable)
            if partbl.shape[0] == parlist.shape[0]:
                partbl = pd.concat([parlist.loc[:, parlist.columns != 'file'].reset_index(drop=True), partbl.reset_index(drop=True)], axis=1)            
                        
            # Add to dictionary        
            ftbl['params'] = partbl
        else:
            print("Warning: Parameter description files not located at specified path. Skipping table creation.")
            ftbl['params'] = None
                    
    print("End of filelist_param()", '\n'*2)
    return ftbl

#%% Call the main function if this is the main script
if __name__ == '__main__':
    
    print("Start of import_param()", '\n'*2)
    
    try:
        args = sys.argv
    except:
        args = [None, None, None, None, None]
    try:
        flist_dict = filelist_param(Path=args[0], Time=args[1], Spat=args[2], Grow=args[3], Ptbl=args[4])
    except:
        flist_dict = None
    
    print("End of filelist_param()", '\n'*2)

#%% Test

# =============================================================================
# file_table = filelist_param(
#     Path=os.path.normpath(r"C:\Ubuntu\rhessys\temp\output\gridmet\1979\1"),
#     Time="yearly",
#     Spat="basin",
#     Grow=False,
#     Ptbl=True
#     )
# =============================================================================
