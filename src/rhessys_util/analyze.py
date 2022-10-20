# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:23:51 2022

@author: jonge
"""

#%% Imports
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

#%% Function to aggregate rhessys output (fluxes, sinks, or sinks-> fluxes)
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
