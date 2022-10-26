# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:41:40 2022

@author: jonge
"""

#%% Import Dependencies
import numpy as np
import pandas as pd

#%% Import Dependencies from RHESSysUtil Modules by editing System path to include rhessys_util
import sys, os
# tar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir, 'rhessys_util'))
tar_dir1 = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir, os.pardir, os.pardir)) # path of rhessys_util
tar_dir1 = r"{}".format(tar_dir1)
sys.path.append(tar_dir1)

tar_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__))) # path of rhessys_util
tar_dir2 = r"{}".format(tar_dir2)
sys.path.append(tar_dir2)


from rhessys_util import util # determine which modules required

#%% Custom Settings
global_args = [os.path.abspath(r"C:/Ubuntu/rhessys/RHESSysUtil/src/scripts/parameterization/Manual/template_program_input_options.csv")]
global_args = [os.path.abspath(r"C:/Ubuntu/rhessys/RHESSysUtil/src/scripts/parameterization/Manual/template2_program_input_options.csv")]
settings_file = global_args[0] # should be first arguement
settings_tsv = False
#%% Define the main function
def main():
    """
    Manual parameterization program; calls on modules `extract`,
    `tidy`, `analyze`, and `visual`. Together this program does the following:
        (1) Extracts RHESSys output data from a directory of output files.
        (2) Formats the data into dataframes (one for each variable).
        (3) Conducts statistical analysis of each variable specified.
        (4) Plots the variables as requested.
        
    Settings for all modules are imported from a single file. For more information,
    refer to the documentation within each individual module.
    
    Returns
    -------
    None.

    """        
    #print("\n"*2,"Start of main()", '\n'*2)
    #%% Set system arguements
    
    global_args = sys.argv
    # print(global_args)
    try:
        settings_file = global_args[1] # should be first arguement
    except:
        print("Error: Program Settings File Provided")
        return None
    try:
        settings_tsv = global_args[2] # should be second arguement
        if settings_tsv.casefold() == "true":
            settings_tsv = True
        elif settings_tsv.casefold() == "false":
            settings_tsv = False
    except:
        settings_tsv = False
        
    print(settings_file)
    print(settings_tsv)
    
    #%% Import program settings from file (script in same dir)    
    progset = util.import_settings(File=settings_file, TSV=settings_tsv)
    
    #%% Filelist construction (script in same dir)
    if progset['filelist']['value'] == True:    
        import filelist_param
        file_dict = filelist_param.filelist_param(
            Path=progset['in_path']['value'], 
            Time=progset['time']['value'], 
            Spat=progset['spat']['value'], 
            Grow=progset['grow']['value'],
            Ptbl = True
            )
    
    #%% Extract data (script in same dir)
    if progset['extract']['value'] == True:
        import extract_param
        data = extract_param.extract_param(
            Filelist=file_dict['files'],            
            Varlist=progset['varlist']['value'], 
            Spat=progset['spat']['value'], 
            Time=progset['time']['value']
            )
    
        #%% Write the Extract data to file     
        if progset['extract_write']['value'] == True:
            outsuffix = ''
            if progset['grow']['value'] == True:
                outsuffix = "".join([outsuffix,"grow"])
            outsuffix = "_".join([outsuffix, progset['spat']['value'], progset['time']['value'] + '.csv'])
            
            outprefix = os.path.abspath(progset['out_path']['value'])
            try:
                os.mkdir(outprefix)
            except OSError as error:
                print(error)
                            
            for var in data:
                outsuffix2 = "".join(['extract_' + var, outsuffix])            
                outfile = os.path.join(outprefix, outsuffix2)
                data[var].to_csv(outfile, index=False)
    
    #%% Tidy data (script in same dir)
    if progset['tidy']['value'] == True:
        import tidy_param
        data = tidy_param.tidy_param(
            Data=data, 
            Agg=progset['agg']['value'], 
            Agg_grp1=progset['agg_grp1']['value'], 
            Agg_grp2=progset['agg_grp2']['value'], 
            Agg_method=progset['agg_method']['value']
            )
                
        #%% Write Tidy data to file
        if progset['tidy_write']['value'] == True:
            outsuffix = ''
            if progset['grow']['value'] == True:
                outsuffix = "".join([outsuffix,"grow"])
            outsuffix = "_".join([outsuffix, progset['spat']['value'], progset['time']['value'] + '.csv'])
            
            outprefix = os.path.abspath(progset['out_path']['value'])
            try:
                os.mkdir(outprefix)
            except OSError as error: # Error produced when it exists; print it
                print(error)
                            
            for var in data:
                outsuffix2 = "".join(['tidy_' + var, outsuffix])            
                outfile = os.path.join(outprefix, outsuffix2)
                data[var].to_csv(outfile, index=False)
            
        
    #%% TODO: Analyze data (script in same dir)
    #import analyze_param
    #analyze_param.analyze_param()
    
    #%% TODO: Visualize data (script in same dir)
    
    #%% Finish Function
    #print("End of main()", '\n'*2)
    return None

#%% Call the main function if this is the main script
if __name__ == '__main__':
    print("\n\nStart of main()", '\n'*2)
    print(sys.argv)
    # Grab command line arguement(s) should be a path to program settings file
    
    # Run Main
    main()
    
    print('\n'*2)
    print("End of main()", '\n'*2)

