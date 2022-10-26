# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:27:55 2022

@author: jonge
"""
import numpy as np
import pandas as pd

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

#%% Function to apply lagged difference to columns of a dataframe
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

#%% Aggregation method switch
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
        df = df.groupby(Group, as_index=False).mean()
    elif agg_method[0] == "sum":
        df = df.groupby(Group, as_index=False).sum()
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

#%% Function to aggregate rhessys output (fluxes, sinks, or sinks-> fluxes)
def agg(Dataframe: pd.DataFrame, Varlist: list, Group1: list, Group2: list, Method: list) -> pd.DataFrame:
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
      
    df = Dataframe.copy()
    
    # Conduct first level aggregation based on `Group1` and `Method[0]`    
    if agg_method[0] != None: # If Method[0] = None then skip
        # Filter dataframe to only include Varlist and Grp1 columns
        keeplist = [item for item in Group1 + Varlist if item != None]
        df = df[keeplist]        
        # Apply 1st stage aggregation
        df = apply_agg(Dataframe=df, Group=Group1, Method=agg_method[0])

    # Conduct second level aggregation based on `Group2` and `Method[1]`
    if agg_method[1] != None:
        keeplist = [item for item in Group2 + Varlist if item != None]        
        df = df[keeplist]
        df = apply_agg(Dataframe=df, Group=Group2, Method=agg_method[1])

    return df

#%% obtain the rolling average of all specified columns of a dataframe
def rollmean():
    print()

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