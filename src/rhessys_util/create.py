# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 16:31:55 2022

@author: jonge
"""

#%% Imports

import numpy as np
import pandas as pd
import os

#%% Create parameter table
def params(Names: list, Const: list = ['Default'], Min: list = ['Default'], 
                 Max: list = ['Default'], Sd: list = ['Default'], Method: list = ['Default'], 
                 Length: int = 10, Write: bool = False, Outfile_path: str = ".", 
                 Outfile_name: str = "Par1", Outfile_type = 'tsv') -> pd.DataFrame:
    """
    Creates a table of parameter values corresponding to the `Names` input, 
    wherein each column has variable values. This dataframe is to be used as 
    input for RHESSys to conduct calibration or sensitivity simulations.
    
    Default Operation values for input Names:\n\t 
        `Const` = [0.5] * len(Names)\n\t
        `Min` = [0.1] * len(Names)\n\t
        `Max` = [1] * len(Names)\n\t
        `Sd` = [0.05] * len(Names)\n
        `Method` = ['Const'] * len(Names)\n\t
        `Length` = 10 (rows)\n\t
        'Outfile_path' = './'\n\t
        `Outfile_name` = 'Par1'\n\t
        `Outfile_type` = 'tsv' tab deliminated\n
        
    Parameter Creation Methods:\n\t
        `'const'`: Repeats `Const` value for all combinations of the paramater.\n\t
        `'seq'`: Creates an equally spaced sequence of length `Length` for the 
            parameter, starting from `Min` and ending at `Max`.\n\t
        `'unif'`: Draws `Length` number of random values from a uniform distribution,
            with bounds defined by `Min` and `Max` for each parameter.\n\t
        `'norm'`: Draws 'Length` number of random values from a normal distribution
            defined by mean (`Const`) and standard deviation ((`Max` - `Min`) * `Sd`).
            

    Parameters
    ----------
    Names : list
        Parameter names.
    Const : list, optional
        Default values associated with each parameter. If the `const` method is used,
        the parameter will take on this value for the duration of `Length`. If the
        `Norm` method is used, this is used as the mean value of the random normal
        distribution. The default is ['Default'].
    Min : list, optional
        Minimum values assicated with each parameter. If `seq` method is used,
        the sequence starts with this value. When `Norm` method is selected, this
        value is used with `Max` and `Sd` to calculate the standard deviation of 
        the parent distribution. The default is ['Default'].
    Max : list, optional
        Maximum values assicated with each parameter. If `seq` method is used,
        the sequence ends with this value. When `Norm` method is selected, this
        value is used with `Min` and `Sd` to calculate the standard deviation of 
        the parent distribution. The default is ['Default'].
    Sd : list, optional
        Standard deviation scalor for each paraeter. During the `Norm` method, 
        the standard deviation is calculated as (Min - Max)*Sd. The default is ['Default'].
    Method : list, optional
        Paramter set creation method. This dictates how the array of paramters associate
        with each `Names` input will be create. See valid method option above. 
        The default is ['Default'].
    Length : int, optional
        Number of parameter values to create for all `Names` parameters. The default is 10.
    Write : bool, optional
        Switch to specify whether or not to write output object to a file.
    Outfile_path : str, optional
        Path specifying where to write the outputfile. The default is ".".
    Outfile_name : str, optional
        Name of the output file. The default is "Par1".
    Outfile_type : str, optional
        Format of output file (i.e tab deliminated or comma deliminated). The default is 'tdl'

    Returns
    -------
    pd.Pa
    Pandas DataFrame of parameter values specified by `Names` of length `Length`.
    Created by using methods `Method` and based on the input function paramters 
    (`Const`, `Min`, `Max`, `Sd`).

    """
    
    # Check if input parameters are valid
    
    ## Names
    if type(Names).__name__ != 'list':
        print("Error: `Names` is not a list.")
        return
    
    if len(Names) < 1:
        print("Error: `Names` must be at least one character long")
        return
    
    ## Const
    if type(Const).__name__ != 'list':
        print("Error: `Const` is not a list.")
        return

    if len(Const) !=  len(Names):
        print("Error: `Const` must be be same length as `Names`")
        return
    
    ltest = [type(item).__name__ in ['int', 'float', 'decimal'] for item in Const]
    if not all(ltest):
        print("Error: `Const` choice, {} is not a number."
              .format(np.array(Const)[ltest]))
        return    
    
    ## Min
    if type(Min).__name__ != 'list':
        print("Error: `Min` is not a list.")
        return

    if len(Min) !=  len(Names):
        print("Error: `Min` must be be same length as `Names`")
        return
    
    ltest = [type(item).__name__ in ['int', 'float', 'decimal'] for item in Min]
    if not all(ltest):
        print("Error: `Min` choice, {} is not a number."
              .format(np.array(Min)[ltest]))
        return    
    
    ## Max
    if type(Max).__name__ != 'list':
        print("Error: `Max` is not a list.")
        return

    if len(Max) !=  len(Names):
        print("Error: `Max` must be be same length as `Names`")
        return
    
    ltest = [type(item).__name__ in ['int', 'float', 'decimal'] for item in Max]
    if not all(ltest):
        print("Error: `Max` choice, {} is not a number."
              .format(np.array(Max)[ltest]))
        return    
    
    ## Sd
    if type(Sd).__name__ != 'list':
        print("Error: `Sd` is not a list.")
        return

    if len(Sd) !=  len(Names):
        print("Error: `Sd` must be be same length as `Names`")
        return
    
    ltest = [type(item).__name__ in ['int', 'float', 'decimal'] for item in Sd]
    if not all(ltest):
        print("Error: `Sd` choice, {} is not a number."
              .format(np.array(Sd)[ltest]))
        return    
    
    ## Method
    if type(Method).__name__ != 'list':
        print("Error: `Method` is not a list.")
        return

    if len(Method) !=  len(Names):
        print("Error: `Method` must be be same length as `Names`")
        return
    
    valid = ['const', 'seq', 'unif', 'norm']
    method = [item.lower() for item in Method]
    ltest = [item in valid for item in method]
    if not all(ltest):
        print("Error: `Method` choice, {} is not a valid option. Choice valid option in function documentation"
              .format(np.array(Method)[ltest]))
    
    ## Length
    if type(Length).__name__ != 'int':
        print("Error: `Length` is not an int.")
        return
    
    if Length <= 0:
        print("Error: `Length` must be greater than or equal to 1.")
        return
    
    ## Write
    if type(Write).__name__ != 'bool':
        print("Error: `Write` is not a bool.")
        return   
    
    pwrite = Write
    
    ## Outfile_path
    if type(Outfile_path).__name__ != 'str':
        print("Error: `Outfile_path` is not a str. `Write is being set to False.")
        pwrite = False
    
    ltest = os.path.exists(Outfile_path)
    if ltest != True:
        print("Error: `Outfile_path` does not exist in this environment. `Write` is being set to False.")
        pwrite = False
    
    ## Outfile_name
    if type(Outfile_name).__name__ != 'str':
        print("Error: `Outfile_name` is not a str. `Write is being set to False.")
        pwrite = False
        
    ## Outfile_type
    if type(Outfile_type).__name__ != 'str':
        print("Error: `Outfile_type` is not a str. `Write is being set to False.")
        pwrite = False
    
    valid = ['tsv', 'csv']
    ltest = Outfile_type in valid
    if ltest != True:
        print("Error: `Outfile_type` {} is not a valid format. `Write` is being set to False."
              .format(Outfile_type))
        pwrite = False
    
    # Save local variables and convert lists to np.arrays 
    pnames = np.array(Names)
    pconst = np.array(Const)
    pmin = np.array(Min)
    pmax = np.array(Max)
    psd = np.array(Sd)
    pmethod = np.array(method)
    plength = Length
    pout_path = Outfile_path
    pout_name = Outfile_name
    pout_type = Outfile_type
    
    # Loop through each parameter in `Name` and create np.array based on `Method`
    ## (i.e) `Const`, `seq`, `unif`, or `norm`    
    plist = list()
    n = len(pnames)
    
    for i in range(0,n):
        print("i : ", i, " | name : ", pnames[i], sep="")
        if pmethod[i] == 'const':
            plist.append(np.full((plength, 1), fill_value=pconst[i]))
        elif pmethod[i] == 'seq':
            plist.append(np.linspace(pmin[i], pmax[i], num=plength)[:, np.newaxis])
        elif pmethod[i] == 'unif':
            plist.append(np.random.uniform(pmin[i], pmax[i], size=plength)[:, np.newaxis])
        elif pmethod[i] == 'norm':
            # Consider changing loc=(pmax[i] + pmin[i])/2 in future
            sd = (pmax[i] - pmin[i])/psd[i]
            plist.append(np.random.normal(loc=pconst[i], scale=sd, size=plength)[:, np.newaxis])
        else:
            print("Error: Invalid method requested.")
            return
        
    # Merge the 1d arrays into a 2d array. Use each array as column to join.
    parr = np.concatenate(plist, axis=1)
    
    # Convert the 2d array into a Pandas Dataframe
    pdf = pd.DataFrame(parr, columns=pnames)

    pdf = pdf.round(decimals = 3)
    
    # If Write == T, write to file based on `Outfilet` and `Outfile_type`
    if pwrite == True:        
        if pout_type == 'tsv':
            poutfile = pout_path + '/' + pout_name + '.txt'
            print("Writing {} to file.".format(poutfile))
            pdf.to_csv(poutfile, sep="\t", header=True, index=False)
                  
        elif pout_type == 'csv':
            poutfile = pout_path + '/' + pout_name + '.txt'
            print("Writing {} to file.".format(poutfile))
            pdf.to_csv(poutfile, header=True, index=False)
        else:
            print("Error: Invalid output file format, failed to write to file.")
    
    return pdf