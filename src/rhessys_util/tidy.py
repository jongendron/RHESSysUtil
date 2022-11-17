# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:27:55 2022

@author: jonge
"""
import numpy as np
import pandas as pd
import warnings

#%% Function to join two dataframes by common columns that are specified
def join_data(Data1: pd.DataFrame, Data2: pd.DataFrame, Group: list) -> pd.DataFrame:
    """    
    Parameters
    ----------
    Data1 : pd.DataFrame
        Datasets that to add external data to.
    Data2 : pd.DataFrame
        Dataset containing external data.
    Group : list
        List of columns to join two tables by.

    Returns
    -------
    pd.DataFrame
        Results of the two joined datasets.

    """        
    # Check that input arguements are valid
    
    ## Check Data1 and Data2 type
    if type(Data1).__name__ != "DataFrame" or type(Data2).__name__ != "DataFrame":
        wmsg = "Warning: `Data1` or `Data2` is not a DataFrame object. Canceling Join procedure."
        warnings.warn(wmsg)
        return Data1
    
    ## Check Group type
    if type(Group).__name__ != "list":
        wmsg = "Warning: `Group` is not a list object. Canceling Join procedure."
        warnings.warn(wmsg)
        return Data1
    
    ## Check Group length
    if len(Group) <= 0:
        wmsg = "Warning: `Group` has insufficient number of elements. Canceling Join procedure."
        warnings.warn(wmsg)
        return Data1
     
    # Check if join will be valid # Warning: Column names are case senitive
    
    ## Check that all join columns exist in both Data1 (Target) and Data2 (external)
    hdr1 = Data1.columns
    hdr2 = Data2.columns
    for item in Group:
        if item not in hdr1 or item not in hdr2:
            wmsg = "Warning: {} is not a column found in `Data1` and or `Data2`. Canceling Join procedure.".format(item)
            warnings.warn(wmsg)
            return Data1
            
    # Perform dataFrame join based on `Join_grp` as the linker columns
    # retains format of Data1 | only adds rows from Data2 if the linker column value exists in Data1
    try:
        df = pd.merge(Data1, Data2, on=Group, how='left', sort=False) # only adds rows from right if the linker value exists in left
    except:
        wmsg = "Warning: Uncertain issue during join between Data1 and Data2. Canceling Join procedure."
        warnings.warn(wmsg)
        return Data1
    
    # return the joined dataset
    return df

#%% Function to compute the lagged difference of a NumPy Array
def lagdiff(Data: np.ndarray) -> np.ndarray:
    
    x = Data.copy()
    
    if type(x).__name__ not in ['ndarray', 'Series']:
        wmsg = "Warning: `Data` type() {} is neither ['ndarray', 'Series']".format(type(Data).__name__)
        warnings.warn(wmsg)
        return

    
    if x.ndim != 1:                
        shp = x.shape
        ltest = [item == 1 for item in shp]
        if any(ltest):            
            x = x.flatten()
        else:
            wmsg("Warning: `Data` is a multi-dimensional array")
            warnings.warn(wmsg)
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
        wmsg = "Warning: Incompatable type for `Data`\n{} is not acceptable".format(type(Data))
        warnings.warn(wmsg)
        return None
    
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
        print("Warning: Incompatable type or structure for 'Data`")
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
    hdr2 = [it.casefold() for it in hdr]
    
    method_list = ['mean', 'sum', 'lagsum', 'min', 'max',
                            '25pct', '50pct', '75pct', '90pct', '99pct']
    
    method_list2 = [it.casefold() for it in method_list]
                
    ## Check Group arguement validity
    group = []        
    for item in Group:
        try:
            group.append(hdr[hdr2.index(item.casefold())])
        except:            
            wmsg = "Warning: {} is not a valid column in the dataset.".format(item)
            warnings.warn(wmsg)
            return None
  
    ## Check Method type
    if type(Method).__name__ != 'str':        
            wmsg = 'Warning: `Method` arguement is not in str format'
            warnings.warn(wmsg)
            return None
            
    ## Check Method argument validity    
    try:
        agg_method = method_list[method_list2.index(Method.casefold())]
    except:
        wmsg = "Warning: {} is an invalid `Method".format(Method)
        warnings.warn(wmsg)
        return None
        
    # Conduct aggregation
    
    df = Dataframe.copy()
    
    if agg_method == "mean":
        df = df.groupby(group, as_index=False).mean()
    elif agg_method == "sum":
        df = df.groupby(group, as_index=False).sum()
    elif agg_method == "lagsum":
        ltest = [item not in Group for item in df.columns]
        df_data = df.columns[ltest].values        
        df[df_data] = apply_lagdiff(df[df_data])
        df = df.groupby(group, as_index=False).sum()
    elif agg_method == "min":
        df = df.groupby(group, as_index=False).min()
    elif agg_method == "max":
        df = df.groupby(group, as_index=False).max()
    elif agg_method == "25pct":
        df = df.groupby(group, as_index=False).quantile(q=0.25)
    elif agg_method == "50pct":
        df = df.groupby(group, as_index=False).median()
    elif agg_method == "75pct":
        df = df.groupby(group, as_index=False).quantile(q=0.75)
    elif agg_method == "90pct":
        df = df.groupby(group, as_index=False).quantile(q=0.90)
    elif agg_method == "99pct":
        df = df.groupby(group, as_index=False).quantile(q=0.99)
    else:
        wmsg = "Warning: Invalid agg_method"
        warnings.warn(wmsg)
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
        elements must be a valid column names found in `Dataframe`. [None] will
        skip this level of aggregation.
        
    Group2 : list
        List of strings for the program to use during stage 2 aggregation. List
        elements must be a valid column names found in `Dataframe`. [None] will
        skip this level of aggreation.
        
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
    hdr2 = [it.casefold() for it in hdr]
    
    method_list = ['mean', 'sum', 'lagsum', 'min', 'max',
                            '25pct', '50pct', '75pct', '90pct', '99pct'] #, None]
    method_list2 = [it.casefold() for it in method_list]
    
    ## Check Varlist type
    if type(Varlist).__name__ != 'list':        
            wmsg = 'Warning: `Varlist` arguement is not in list format'
            warnings.warn(wmsg)
            return None
    
    # Check Varlist validity
    if Varlist != [None]:
        varlist = []
        for item in Varlist:
            try:
                varlist.append(hdr[hdr2.index(item.casefold())])
            except:
                wmsg = "Warning: {} is not a valid column in the dataset.".format(item)
                warnings.warn(wmsg)
                return None
    else:
        wmsg = "Warning: No Variables selected for aggregation. Returning original dataframe"
        warnings.warn(wmsg)
        return Dataframe
    
    ## Check Group1 type
    if type(Group1).__name__ != 'list':
        wmsg = 'Warning: `Group1` arguement is not in list format'
        warnings.warn(wmsg)
        return None
    
    ## Check Group1 arguement validity
    if Group1 != [None]:
        group1 = []             
        for item in Group1:
            try:
                group1.append(hdr[hdr2.index(item.casefold())])
            except:                
                wmsg = "Warning: {} is not a valid column in the dataset.".format(item)
                warnings.warn(wmsg)
                return None
    else:
        group1 = [None]
    
    ## Check Group2 type
    if type(Group2).__name__ != 'list':        
            wmsg = 'Warning: `Group2` arguement is not in list format'
            warnings.warn(wmsg)
            return None
    
    ## Check Group2 arguement validity
    if Group2 != [None]:
        group2 = []
        for item in Group2:
            try:
                group2.append(hdr[hdr2.index(item.casefold())])
            except:
                wmsg = "Warning: {} is not a valid column in the dataset.".format(item)
                warnings.warn(wmsg)
                return None
    else:
        group2 = [None]
        
    ## Check that all of Group2 arguements are found in Group1 if both groups are not None
    ## if they are not, then add them to it
    if group1 != [None] and group2 != [None]:
        for item in group2:
            if item not in group1:
                wmsg = "Warning: {0} is in group2 but not group1. Adding {0} to group1.".format(item)
                warnings.warn(wmsg)
                group1.append(item)
    
    ## Check Method type
    if type(Method).__name__ != 'list':        
            wmsg = 'Warning: `Method` arguement is not in list format'
            warnings.warn(wmsg)
            return
    
    ## Check Method length        
    if len(Method) == 0:
        wmsg = "Warning: No arguemnets provided to `Method`."
        warnings.warn(wmsg)
        return None
    elif len(Method) == 1:
        wmsg = "Only one arguement provided to `Method`, assuming method for stage 1\aggregation is `None`"
        warnings.warn(wmsg)
        Method2 = [None] + Method
    elif len(Method) == 2:
        Method2 = Method
    else:
        wmsg = "Warning: `Method` argument has too many elements. Only provide 2"
        warnings.warn(wmsg)
        return  None                 
    
    ## Check Method argument validity
    agg_method = []    
    for item in Method2:
        if item != None:        
            try:
                agg_method.append(method_list[method_list2.index(item.casefold())])
            except:
                wmsg = "Warning: {} is not a valid method.".format(item)
                warnings.warn(wmsg)
                return None
        else:
            agg_method.append(None)
            
    # Copy the input dataset
    df = Dataframe.copy()
    
    # Conduct first level aggregation based on `Group1` and `Method[0]`    
    if agg_method[0] != None: # If Method[0] = None then skip
        
        ## Filter dataframe to only include varlist and group1 columns        
        keeplist0 = [item for item in (group1 + varlist) if item != None] # make sure no duplicates
        #keeplist = [*set(keeplist)]        
        keeplist = []
        [keeplist.append(item) for item in keeplist0 if item not in keeplist]
        del keeplist0
        df = df[keeplist]        
        
        ## Apply 1st stage aggregation        
        df = apply_agg(Dataframe=df, Group=group1, Method=agg_method[0])

    # Conduct second level aggregation based on `Group2` and `Method[1]`
    if agg_method[1] != None:        
        
        ## Filter dataframe to only include varlist and group2
        keeplist0 = [item for item in (group2 + varlist) if item != None]
        #keeplist = [*set(keeplist)]
        keeplist = []
        [keeplist.append(item) for item in keeplist0 if item not in keeplist]                        
        del keeplist0
        df = df[keeplist]
        
        
        # Apply 2nd stage aggregation
        df = apply_agg(Dataframe=df, Group=group2, Method=agg_method[1])

    return df

#%% obtain the rolling average of all specified columns of a dataframe
def rollmean(Data: pd.DataFrame, Varlist: list, K: int = 3, Group: list = [None]) -> pd.DataFrame:
    """
    Calculates the rolling average of specified columns of a Pandas DataFrame,
    using `K` as a the window length.

    Parameters
    ----------
    Data : pd.DataFrame
        DataFrame to perform rolling mean on.
    Varlist : list
        Columns of `Data` to performn rolling mean on.
    K : int
        Window length for rolling mean procedure. Default is 3.
    Group : list
        List of columns to group `Data` by for Rollmean operation. The rolling mean
        is then calculated for all rows in each group.

    Returns
    -------
    pd.DataFrame
        Modified version of `Data` with rolling mean for columns specified by `Varlist`.

    """
    # Check validity of arguements
    
    ## Check Data type
    if type(Data).__name__ != "DataFrame":
        wmsg = "Warning: `Data` is not of type DataFrame. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    ## Check that Data is not empty
    if Data.empty:
        wmsg = "Warning: `Data` is an empty DataFrame. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    ## Check Varlist type
    if type(Varlist).__name__ != 'list':
        wmsg = "Warning: `Varlist` is not of type `list`. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    ## Check that Varlist elements exist as columns in Data
    hdr = Data.columns
    hdr2 = [it.casefold() for it in hdr]
    
    varlist = []
    for item in Varlist:
        try:
            varlist.append(hdr[hdr2.index(item.casefold())])
        except:
            wmsg = f"Warnings: {item} is not a valid column in Data. Canceling Rollmean procedure."
            warnings.warn(wmsg)
            return Data
    
    ## Check K type    
    if type(K).__name__ != 'int':
        wmsg = "Warning: `K` is not of type `int`. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    ## Check Group type
    if type(Group).__name__ != 'list':
        wmsg = "Warning: `Group` is not of type `list`. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    ## Check that Group elements exist as columns in Data if [None] is not specified
    group = []
    if Group != [None]:
        for item in Group:
            try:
                group.append(hdr[hdr2.index(item.casefold())])
            except:
                wmsg = f"Warnings: {item} is not a valid column in Data. Canceling Rollmean procedure."
                warnings.warn(wmsg)
                return Data
    else:
        group = [None]
    
    # Calculate rolling mean    
    
    
            
    ## find columns in hdr that are not in group or varlist (idx)
    idx = [item for item in hdr if item not in (group + varlist)]
    idx2 = [it.casefold() for it in idx]
    
    ## separate temporal items in idx from non-temporal items and sort temporal items by decreasing magntiude 
    ## (syr > year > smth > month > sday > day)
    ttmp = ['sdec', 'dec', 'syr', 'year', 'smth', 'month', 'sday', 'day'] # ordered list for time    
    idx_time = []    
    for item in ttmp:
        try:
            idx_time.append(idx[idx2.index(item)])
        except:
            pass
    
    ## Identify non-temporal items
    idx_ntime = [it for it in idx if it not in idx_time]    
    
    ## Merge the two lists
    idx = idx_time + idx_ntime
    
    ## Set dataframe indexes as all spat-time columns not found in group or varlist    
    idx_reset = [it for it in (idx + group) if it != None] # columns in idx and group, but not equal to none    
    
    try:
        df = Data.copy().set_index(idx)
    except:
        df = Data.copy() # no extra spat-time columns 
        
    ## Group data if specified
    if group != [None]:
        df = df.groupby(group, sort=False, as_index=False) # don't sort or use as index
    
    try:
        #df[Varlist] = df[varlist].rolling(K).mean().reset_index(drop=False).sort_values('index').reset_index(drop=True) # unsorted groups
        #df = df.rolling(K).mean().reset_index(drop=False) # retrieve indexes back to columns and sorts data by group
        df = df.rolling(K).mean().reset_index(drop=False).sort_values(idx_reset).reset_index(drop=True) # retrieve indexes to columns and sorts by spat-time and group
        
    except:
        wmsg = "Warning: Rollmean procedure failed unexpectedly. Canceling Rollmean procedure."
        warnings.warn(wmsg)
        return Data
    
    return df
    
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
        wmsg = "Warning: `Groups` is not a list."
        warnings.warn(wmsg)
        return
    
    if len(Groups) < 1:
        wmsg = "Warning: Must group by at least one valid column."
        warnings.warn(wmsg)
        return
        
    ltest = [item in hdr for item in Groups]
    if not all(ltest):
        wmsg = "Warning: `Group` choice, {} is not valid.".format(np.array(Groups)[ltest])
        warnings.warn(wmsg)
        return    
    
    if type(ID).__name__ != 'str':
        wmsg = "Warning: `ID` is not a string."
        warnings.warn(wmsg)
        return
    
    if len(ID) < 1:
        wmsg = "Warning: `ID` must be at least one character long"
        warnings.warn(wmsg)
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
        wmsg = "Warning: Temporal scale, {}, is not a valid option.".format(Time)
        warnings.warn(wmsg)
        return
    
    if Random not in [True, False]:
        wmsg = "Warning: Invalid selection for `Random` flag."
        warnings.warn(wmsg)
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
                wmsg = "Warning: Invalid hier_method object in use, breaking function."
                warnings.warn(wmsg)
                return None
            
        elif hier_method[i] == 2: # days per year
            df[hier_sname[i]] = np.floor(df[hier_sname[i]]/365.25).astype(int) + 1  
            
        elif hier_method[i] == 3: # group by syr and get index
            df = grpidx(Dataframe=df, Groups=['syr','month'], ID='smth')     # month must be available though
            
        else:
            wmsg = "Warning: Invalid hier_method object in use, breaking function."
            warnings.warn(wmsg)
            return None
    
    return df