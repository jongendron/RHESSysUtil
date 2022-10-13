# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 10:14:05 2022

@author: PETBUser
"""
#%% Load Dependencies
import os
import numpy as np
import pandas as pd
import ntpath as nt

#%% Create Pandas DataFrame containing list RHESSys output files and filename identifiers
## Files extracted from specified directory tree (parent path -> down)

def create_filelist(Path: str, Delim: str, ID_loc: list, inc_patn: list, ex_patn: list) -> pd.DataFrame:
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

def read_header(File: str) -> list:
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

# hdr0 = read_header(FILELIST[0])


# print(any('gw' in item for item in hdr))
# VARLIST = ['year', 'month', 'day', 'stor', 'streamflow', 'precip']
# VARLIST = [item1 for item1 in hdr for item2 in VARLIST if item2 in item1]
# print(VARLIST)


#%% Load in RHESSys output file based on spatial scale, temporal scale, and variable list

def read_rhessys(File: str, Spat: str, Time: str, Varlist: list, Bounds: list = [None,None]) -> pd.DataFrame:
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
    hdr = np.array(read_header(File = File))    
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

#df0 = read_rhessys(File=FILELIST[0], Spat='basin', Time='daily', Varlist=['streamflow', 'evap', 'trans'])

#%% Create Group index number for all groups in a dataframe (unstable)

#def idrng(x):
#    #a = np.arange(x[0],(x[1] + 1))
#    return a

def format_grpidx(Dataframe: pd.DataFrame, Groups: list, ID: str = "GroupID") -> pd.DataFrame:
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

### Testing

# =============================================================================
# # See how if rows repeat after a few unique groups they take on the previous groups value
# dict1 = {
#     'a' : [1980, 1980, 1980, 1970, 1970, 1970, 1950, 1950, 1950, 1980, 1980, 1980],
#     'b' : [2, 2, 2, 1, 1, 1, 3, 3, 3, 2, 2, 2],
#     'c' : [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
#     }
# 
# d1 = pd.DataFrame(dict1)
# format_grpidx(Dataframe=d1, Groups=['a','b'], ID='d')
# 
# # See how if rows repeat after a few unique groups they take on new group value
# dict1 = {
#     'a' : [1980, 1980, 1980, 1970, 1970, 1970, 1950, 1950, 1950, 1980, 1980, 1980],
#     'b' : [2, 2, 2, 1, 1, 1, 3, 3, 3, 4, 4, 4],
#     'c' : [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3]
#     }
# 
# d1 = pd.DataFrame(dict1)
# format_grpidx(Dataframe=d1, Groups=['a','b'], ID='d')
# =============================================================================


#%% Format time

def format_simtime(Dataframe: pd.DataFrame, Time: str, Random: bool) -> pd.DataFrame:
    """
    !!! Currently incorrect aggregation !!!
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
            df = format_grpidx(Dataframe=df, Groups=['syr','month'], ID='smth')     # month must be available though
            
        else:
            print("Error: Invalid hier_method object in use, breaking function.")
            return
    
    return df

#df2 = format_simtime(Dataframe=df0, Time='yearly', Random=True)

#%% Function to calculate lagged difference

# For a 1 dimemsional numpy array or pandas dataframe component, calculate
# the lagged difference of all elements

def apply_lagdiff(Data: object) -> object:
    """
    Computes the lagged difference of `Data`. The structure of `Data` is preserved,
    there if `Data` is a 1d NumPy arrays, the `return` will be a 1d array. Likewise,
    if `Data` is a Pandas DataFrame or 2d NumPy array, then the `return` will be
    an object of the same type() and with the same size in axis 1 (columns).
    
        Valid `Data` types include:
            'numpy.ndarray'\n
            'pandas.core.frame.DataFrame'\n
            'pandas.core.series.Series'\n
            
    *DataFrames and multi-dimensional NumPy arrays must only contain data that is
    a number format (int, float, long, etc), otherwise error is thrown.

    Parameters
    ----------
    Data : object
        Numpy array (1d or 2d) or Pandas DataFrame object in which the lagged
        difference will be computed.

    Returns
    -------
    object
        Modified `Data` object, wherein the lagged difference of all elements is
        computed for either a single dimension (1d NumPy array) or in axis 1 
        (2d NumPy array or Pandas DataFrame).

    """
    # Check if Data type is valid
    if type(Data).__name__ not in ['ndarray', 'DataFrame', 'Series']:
        print("Error: Incompatable type for `Data`\n{} is not acceptable".format(type(Data)))
        return
    
    # Apply lag difference function
    x = Data
    
    if (type(x).__name__ == 'ndarray' or type(x).__name__ == 'Series'):
        if x.ndim == 1:
            y = lagdiff(x)
        else:
            shp = x.shape
            ltest = [item == 1 for item in shp]
            if any(ltest):            
                y = lagdiff(x)
            else:
                y = np.apply_along_axis(lagdiff, axis=0, arr=x)
    
    elif type(Data).__name__ == 'DataFrame':
        col_names = x.columns
        y = pd.DataFrame(np.apply_along_axis(lagdiff, axis=0, arr=x), columns=col_names)        
    else:
        print("Error: Incompatable type or structure for 'Data`")
        return
    
    return y

# =============================================================================
# # Testing
# 
# a1 = np.random.randint(low=0, high=20, size=9).reshape((3,3))
# apply_lagdiff(a1)
# 
# df1 = pd.DataFrame(a1, columns=['a', 'b', 'c'])
# apply_lagdiff(df1)
# =============================================================================


#%% Function to compute the lagged difference of a NumPy Array

def lagdiff(Data: np.ndarray) -> np.ndarray:
    
    x = Data.copy()
    
    if type(x).__name__ not in ['ndarray', 'Series']:
        print("Error: `Data` type() {} is neither ['ndarray', 'Series']".format(type(Data).__name__))
        return

    
    if x.ndim != 1:                
        shp = x.shape
        ltest = [item == 1 for item in shp]
        if any(ltest):            
            x = x.flatten()
        else:
            print("Error: `Data` is a multi-dimensional array")
            return None
        
    ytmp = np.pad(x.astype(float), pad_width=1, constant_values=(np.nan,))
    y2 = ytmp[:-1].copy()
    y1 = ytmp[1:].copy()
    y = (y1 - y2)[:-1].copy()
        
    return y
        
# Testing
#a1 = np.array([10,5,1,3])
#lagdiff(a1)
#a2 = np.random.randint(low=0, high=20, size=9).reshape((3,3))
#df0 = pd.DataFrame(a2, columns=['a', 'b', 'c'])
#np.apply_along_axis(lagdiff, axis=0, arr=df0)

#%% Dataframe aggregation application function

# Function that works as a switch for different aggregation methods of a Dataframe

def apply_agg(Dataframe: pd.DataFrame, Group: list, Method: str) -> pd.DataFrame:
    """
    Groups `Dataframe` by `Group` and applies a built-in Pandas aggregation function
    defined by `Method`. Essentially works as a switch for different aggregation
    methods of Pandas DataFrame objects.

    Parameters
    ----------
    Dataframe : pd.DataFrame
        The dataframe to be grouped by `Group` and then have aggregation method
        `Method` applied to.
    Group : list
        List of columns to be used to group `Dataframe`. List elements are only
        valid if they are existing columns of the `Dataframe`.
    Method : str
        The aggregation method to be applied to `Dataframe` after it is grouped
        by `Group`.
        
        Valid Arguements for `Method`:
            `"mean"` = computes average value of each group.\n
            `"sum"` = computes sum of each group.\n
            `"lagsum"` = computes the lagsum of each group (see `lagsum()`).\n
            `"min"` = computes the minimum value of each group.\n
            `"max"` = computes the maximum value of each group.\n
            `"25pct"` = computes the 25th percentile of the group.\n
            `"50pct"` = computes the 50th percentile (median) of the group.\n
            `"75pct"` = computes the 75th percentile of the group.\n
            `"90pct"` = computes the 90th percetnile of the group.\n
            `"99pct"` = comptues the 99th percetnile of the group.\n
            
    Returns
    -------
    pd.DataFrame
        Dataframe containing aggregation values of former `Dataframe`.

    """
    # First check if input arguements are valid
    hdr = Dataframe.columns.values
    method_list = ['mean', 'sum', 'lagsum', 'min', 'max',
                            '25pct', '50pct', '75pct', '90pct', '99pct']
    #tmp = Method
    # agg_method = [tmp]
    agg_method = [Method]
    
    ## Group
    ltest = [item in hdr for item in Group] # Check which elements aren't in hdr    
    if not all(ltest):
        print("Error: Some or all `Group` elements are not valid.\nInvalid elements: {}"
              .format(np.array(Group)[ltest]))
        return
    
    ## Method Length (Method->agg_method)
    if len(agg_method) != 1:
        print("Error: Either no arguements or too many arguements provided to `Method`.")
        return
    
    ## Method arguments
    ltest = [item in method_list for item in agg_method]
    if not all(ltest):
        print("Error: `Method`, {} is not a valid choice."
              .format(np.array(agg_method)[ltest]))
        return    
    
    # Conduct aggregation
    
    df = Dataframe.copy()
    
    if agg_method[0] == "mean":
        df = df.groupby(Group, as_index=False, ).mean()
    elif agg_method[0] == "sum":
        df = df.groupby(Group, as_index=False, ).sum()
    elif agg_method[0] == "lagsum":
        ltest = [item not in Group for item in df.columns]
        df_data = df.columns[ltest].values        
        df[df_data] = apply_lagdiff(df[df_data])
        df = df.groupby(Group, as_index=False).sum()
    elif agg_method[0] == "min":
        df = df.groupby(Group, as_index=False).min()
    elif agg_method[0] == "max":
        df = df.groupby(Group, as_index=False).max()
    elif agg_method[0] == "25pct":
        df = df.groupby(Group, as_index=False).quantile(q=0.25)
    elif agg_method[0] == "50pct":
        df = df.groupby(Group, as_index=False).median()
    elif agg_method[0] == "75pct":
        df = df.groupby(Group, as_index=False).quantile(q=0.75)
    elif agg_method[0] == "90pct":
        df = df.groupby(Group, as_index=False).quantile(q=0.90)
    elif agg_method[0] == "99pct":
        df = df.groupby(Group, as_index=False).quantile(q=0.99)
    else:
        print("Error: Invalid agg_method")
        return None
    
    return df

# =============================================================================
# n = len(datalist)
# for i in range(0,n):
#     dftmp = (
#         datalist[i]
#         .assign(
#             )
#         .assign(sday = lambda x: range(1,(len(datalist[i]) + 1)))
#         .assign(syr = lambda x: m.floor(datalist['sday']/365.25) + 1)
#         .assign()
#         )
# =============================================================================

#%% Aggregate state variables as fluxes, sinks, or sinks-> fluxes


# Create a switch function that will do the previous modifications to a dataframe
# --> create another function that will calculate the lagged_difference of df columns
# (ex) if you want average monthly precipitation for each year then ...
# first aggregate to (month, year) with sum
# then aggregate to (year) with average

def format_agg(Dataframe: pd.DataFrame, Varlist: list, Group1: list, Group2: list, Method: list) -> pd.DataFrame:
    """
    Function to aggregate RHESSys model output. Takes a Pandas dataFrame containing
    RHESSys output and conducts a two stage aggregation processes: 
        
    1. Stage one will aggregate data grouped by columns defined in `Group1` 
    using the method defined by the first element of `Method` (list of size 2).
    
    2. Stage two will take results of stage one, and then aggregate by groups
    defined in `Group2` and the second element of `Method`.
         
    If None is used an an input for `Group1` or `Group2` no aggregation is 
    conducted at the associated stage. For example, if `Group1` is equal to
    `None`, then stage 1 aggregation is skipped, and the function proceeds 
    to the stage 2 aggregation.
         

    Parameters
    ----------
    Dataframe : pd.DataFrame
        Pandas Dataframe containing RHESSys model output in wide-format.
        
    Varlist : list
        List of strings for the program to use to filter `Dataframe` before the
        aggregation. List elements msut be a valid column name found in `Dataframe`.
        User does not need to include variabels defined in `Group1` or `Group2`
    
    Group1 : list
        List of strings for the program to use during stage 1 aggregation. List
        elements must be a valid column names found in `Dataframe`.
        
    Group2 : list
        List of strings for the program to use during stage 2 aggregation. List
        elements must be a valid column names found in `Dataframe`. 
        
    Method : list (length 2)
        List containing the aggregation methods for stage 1 and stage 2. 
        
        Valid Arguements for `Method`:
            `"mean"` = computes average value of each group.\n
            `"sum"` = computes sum of each group.\n
            `"lagsum"` = computes the lagsum of each group (see `lagsum()`).\n
            `"min"` = computes the minimum value of each group.\n
            `"max"` = computes the maximum value of each group.\n
            `"25pct"` = computes the 25th percentile of the group.\n
            `"50pct"` = computes the 50th percentile (median) of the group.\n
            `"75pct"` = computes the 75th percentile of the group.\n
            `"90pct"` = computes the 90th percetnile of the group.\n
            `"99pct"` = comptues the 99th percetnile of the group.\n
            
    Returns
    -------
    pd.DataFrame
        Reformated Pandas Dataframe containing aggregated data.

    """
    
    # Test if input arguemnets are valid
    hdr = Dataframe.columns.values
    method_list = ['mean', 'sum', 'lagsum', 'min', 'max',
                            '25pct', '50pct', '75pct', '90pct', '99pct'] + [None]
    
    ## Varlist
    if type(Varlist).__name__ != 'list':        
            print('Error: `Varlist` arguement is not in list format')
            return
    ltest = [item in hdr for item in Varlist]    
    if not all(ltest):
        print("Error: Some or all `Varlist` elements are not valid.\nInvalid elements: {}"
              .format(np.array(Varlist)[ltest]))
        return    
    
    ## Group1
    if type(Group1).__name__ != 'list':
        print('Error: `Group1` arguement is not in list format')
        return
    if Group1 != [None]:
        ltest = [item in hdr for item in Group1] # Check which elements aren't in hdr    
        if not all(ltest):
            print("Error: Some or all `Group1` elements are not valid.\nInvalid elements: {}"
                  .format(np.array(Group1)[ltest]))
            return    
    
    ## Group2
    if type(Group2).__name__ != 'list':        
            print('Error: `Group2` arguement is not in list format')
            return
    if Group2 != [None]:
        ltest = [item in hdr for item in Group2] # Check which elements aren't in hdr    
        if not all(ltest):
            print("Error: Some or all `Group2` elements are not valid.\nInvalid elements: {}"
                  .format(np.array(Group2)[ltest]))
            return    
    
    ## Method Length (Method->agg_method)
    if type(Method).__name__ != 'list':        
            print('Error: `Method` arguement is not in list format')
            return
    if len(Method) == 0:
        print("Error: No arguemnets provided to `Method`.")
        return
    elif len(Method) == 1:
        print("Only one arguement provided to `Method`, assuming method for stage 1\aggregation is `None`")
        agg_method = [None] + Method
    elif len(Method) == 2:
        agg_method = Method
    else:
        print("Error: `Method` argument has too many elements. Only provide 2")
        return                  
    
    ## Method arguments
    ltest = [item in (method_list) for item in agg_method]
    if not all(ltest):
        print("Error: Some or all `Method` elements are not valid.\nInvalid elements: {}"
              .format(np.array(Method)[ltest]))
        return    
    
    # Filter the Dataframe to only include Varlist columns and those needed by
    # stage 1 (`Group1`) and stage 2 (`Group2`) aggregations, and remove duplicates    
    keeplist = Group1 + Group2 + Varlist
    keeplist = list(dict.fromkeys(keeplist)) # WARNING: Order is only preserved for python 3.7 & up
    keeplist = list(filter(lambda item: item is not None, keeplist))
    
    df = Dataframe[keeplist].copy()
    
    # Conduct first level aggregation based on `Group1` and `Method[0]`
    # If Method[0] = None then skip
    if agg_method[0] != None:
        df = apply_agg(Dataframe=df, Group=Group1, Method=agg_method[0])

    # Conduct second level aggregation based on `Group2` and `Method[1]`
    if agg_method[1] != None:
        df = apply_agg(Dataframe=df, Group=Group2, Method=agg_method[1])

    return df

#%%
# =============================================================================
# vlist = ['sat_def_z', 'rz_storage', 'unsat_stor']
# column_list = read_header(FILELIST[0])
# df0 = read_rhessys(FILELIST[0], Spat='basin', Time='daily', Varlist=['sat_def_z', 'rz_storage', 'unsat_stor'])
# df2 = format_simtime(Dataframe=df0, Time='daily', Random=True)
# format_agg(df2, Varlist=vlist, Group1=[None], Group2=['syr'], Method=[None,'lagsum'])
# =============================================================================

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


#%% Function to Extract Variable Output From a list of files

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
        dat = read_rhessys(File=Filelist[i], Spat=Spat, Time=Time, Varlist=Varlist, Bounds=Bounds)
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

#%% Test


# =============================================================================
# VARLIST = ['overland_flow', 'denitrif']
# BOUNDS = [None,None]
# SPAT = "patch"
# TIME = "yearly"
# GROWTH = False
# RANDOM = True # if simulation Time comes from random year module (by Min)
# 
# FILEPATH = "./initialization/output/test2"
# filelist = create_filelist(Dir=FILEPATH, Spat=SPAT, Time=TIME, Growth=GROWTH)
# taglist = [nt.basename(item).split("_")[0] for item in filelist]
# 
# dlist = merge_sims(Filelist=filelist, Varlist=VARLIST, Bounds=BOUNDS, Spat=SPAT, Time=TIME, Random=True)
# =============================================================================

#%% To apply rolling mean to columns in place
# will use as little as few as x rows to calculate rolling mean if  min_periods=x

# =============================================================================
# df = dlist[1]
# tmp = [col not in ['year', 'patchID'] for col in df.columns]
# tmp = df.columns[tmp]
# df2 = df.copy()
# df2[tmp] = df2[tmp].rolling(5,1).mean()
# print(df,'\n\n')
# print(df2)
# 
# =============================================================================
# Still need a function to calculate NSE, R2, RMSE, %BIAS, ETC for a wide dataframe
# \ No newline at end of file

#%% Get RHESSys output filelist (archived)

# =============================================================================
# def create_filelist(Dir: str, Spat: str, Time: str, Growth: bool) -> list:
#     """
#     Create a list of RHESSys output files based on the specified 'Spat', 'Time', 
#     and `Growth` arguements for directory `Dir`.
# 
#     Parameters
#     ----------
#     Dir : str
#         Directory from which to query for RHESSys output files.
#         
#     Spat : str
#         Spatial scale of RHESSys output files to query, including either:
#             (1) "basin", (2) "zone", (3) "hillslope", (4) "patch", (5) "stratum"
#         
#     Time : str
#         Temporal scale of RHESSsy output files to query, including either:
#             (1) "daily", (2) "monthly", or (3) "yearly".
#             
#     Growth : bool
#         Flag that specifies whether or not to search for growth output files.
# 
#     Returns
#     -------
#     list :
#         List of file paths to RHESSys output files based on `Dir`, 'Spat', 
#         `Time`, and `Growth` arguements. Paths are absolute not relative.
# 
#     """
#     if Spat not in ['basin', 'hillslope', 'zone', 'patch', 'stratum']:
#         print("Error: Spatial scale, {}, is not a valid option".format(Spat))
#         return 0
#     
#     if Time not in ['daily', 'monthly', 'yearly']:
#         print("Error: Temporal scale, {}, is not a valid option".format(Time))
#         return 0
#     
#     if Growth not in [True, False]:
#         print("Error: Growth flag, {}, is not a valid option".format(Growth))
#         return 0
#     
#     npath = os.path.abspath(Dir)
#     flist = os.listdir(npath)
#     flist = [npath + '\\' + s for s in flist]
#     
#     if Growth == False:
#         flist = [s for s in flist if (Spat + "." + Time) in s and "grow" not in s]
#     else:
#         flist = [s for s in flist if ("grow_" + Spat + "." + Time) in s]
#     
#     return flist
# =============================================================================
    

