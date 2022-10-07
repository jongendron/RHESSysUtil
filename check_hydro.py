# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 11:23:40 2022

@author: PETBUser
"""
#%% Load Dependencies
import functions_postprocessing_1 as rh
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# VARLIST = [
#     "pch_pcp", "pch_et", "pch_streamflow", "pch_return_flow", "pch_base_flow",
#     "hill_base_flow", "pch_gw_drainage", "pch_rz_storage", "pch_unsat_storage",
#     "hill_gw_storage"]
# 
# P1LIST = VARLIST
# =============================================================================

VARLIST = ["precip",
            "et",
            "streamflow",
            "base_flow",
            "return_flow",
            "overland_flow",
            "nday_sat",
            "nday_sat70",
            "rz_storage",
            "unsat_storage",
            "gw_drainage",           
            "soilc",
            "soiln",
            "plantc",
            "plantn",
            "lai",
            "psn",
            "denitrif"
            ]

FLUXLIST = ["streamflow",
            "base_flow",
            "return_flow",
            "overland_flow"
            "et",
            "nday_sat",
            "nday_sat70",
            "psn",
            "denitrif"
            ]

STORELIST = ["rz_storage",
              "unsat_storage",
              "gw_storage",
              "soilc",
              "soiln",
              "plantc",
              "plantn",
              "lai"
              ]

P1LIST = ["streamflow", "base_flow", "return_flow", "overland_flow", "gw_drainage", "rz_storage", "unsat_storage", "gw_storage"]
P2LIST = ["soilc","plantc","lai","psn","denitrif"]

# VARLIST =['streamflow', 'evap', 'trans']

#%% Gather Filelist
# flist = rh.create_filelist(Dir="./initialization/output/soil", Spat="basin", Time="daily", Growth=False)
# flist = rh.create_filelist(Dir="./initialization/output/soil", Spat="hillslope", Time="yearly", Growth=False)
flist = rh.create_filelist(Dir="./initialization/output/soil", Spat="patch", Time="yearly", Growth=False)

flist = [item for item in flist if "init_warm" in item] # for filtering by "test_cold"

tlist = [tag.split(sep="\\")[-1].split(sep="_")[3] for tag in flist]

#%% Gather Data and format
datalist = []
for i in range(0,len(flist)):
    file = flist[i]
    print(file + '\n'*2)
    
    # basin daily -> syr
    # dtmp = rh.read_rhessys(File=file, Spat='basin', Time='daily', Varlist=VARLIST)    
    # dtmp = rh.format_simtime(Dataframe=dtmp, Time='daily', Random=True)        
    #dtmp = rh.format_agg(Dataframe=dtmp, Varlist=VARLIST, Group1=[None], Group2=['syr'], Method=[None,'sum'])
    #dtmp = rh.format_agg(Dataframe=dtmp, Varlist=VARLIST, Group1=[None], Group2=['syr','smth'], Method=[None,'sum'])
    
    # hillslope yearly    
    # dtmp = rh.read_rhessys(File=file, Spat='hillslope', Time='yearly', Varlist=VARLIST)
    # dtmp = rh.format_simtime(Dataframe=dtmp, Time='yearly', Random=True)
    
    # patch yearly
    dtmp = rh.read_rhessys(File=file, Spat='patch', Time='yearly', Varlist=VARLIST)
    dtmp = rh.format_simtime(Dataframe=dtmp, Time='yearly', Random=True)    
    
    datalist.insert(i, dtmp)
    datalist[i]['tag'] = tlist[i]
    
df00 = pd.concat(datalist, axis=0)


#%% Write the file

# df00.to_csv('./gw1_comp_basin_yearly',index=False)
# df00.to_csv('./gw1_comp_mo',index=False)
# df00.to_csv('./gw1_comp_patch_yearly.txt', index=False)

# df00.to_csv('./wbal_gw1_0.01_hillslope.yearly', index=False)
df00.to_csv('./wbal_gw1_0.01_patch.yearly', index=False)

#%% Plot 1

for i in range(0,len(P1LIST)):
    var = P1LIST[i]
    df = df00.copy()    
    df.set_index('syr', inplace=True)
    df.groupby('tag')[var].plot(legend=True)
    plt.xlabel('Simulation Year')
    plt.ylabel(var)
    plt.show()   

#%% Plot 2

for i in range(0,len(P2LIST)):
    var = P2LIST[i]
    df = df00.copy()    
    df.set_index('syr', inplace=True)
    df.groupby('tag')[var].plot(legend=True)
    plt.xlabel('Simulation Year')
    plt.ylabel(var)
    plt.show()   

#%% Plot 3

for i in range(0,len(VARLIST)):
    var = VARLIST[i]
    df = df00.copy()    
    df.set_index('syr', inplace=True)
    df.groupby('tag')[var].plot(legend=True)
    plt.xlabel('Simulation Year')
    plt.ylabel(var)
    plt.show()    
    

