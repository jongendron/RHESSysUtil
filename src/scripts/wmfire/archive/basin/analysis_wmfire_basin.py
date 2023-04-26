import sys, os, pathlib
import numpy as np
import pandas as pd

print(sys.argv)
#%% Program settings
file_data = sys.argv[1]
outdir_data=sys.argv[2]
syr_data = sys.argv[3]
mod_data = sys.argv[4]
typ_data = sys.argv[5]
#file_data="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/CSIRO/brw/storage/wmfire_basin_filelist.txt"
#outdir_data="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/CSIRO/brw/storage"
#syr_data=2075
#mod_data="CSIRO"
#typ_data="rcp85"

thresh = 60   # 60 patches (ha)
barea = 27871 # 27871 patches (ha) in basin
#orig = datetime.strptime('1900-01-01', "%Y-%m-%d")

#%% Load the filelist
flist = pd.read_csv(file_data, delim_whitespace=True).rename(columns={'i2':'wmfire_seed'})

#%% Start looping through files
dat = [] # empty list

print("\n\n\n")

for i in range(0,flist.shape[0]):
    print(f"Iteration: {i}\n")       
    
    #%% Load data    
    i0 = flist.iloc[i,0]
    i1 = flist.iloc[i,1]
    wmfire_seed = flist.iloc[i,2]
    file = flist.iloc[i,3]
    
    tdat = pd.read_csv(file)
    tyrs = (1 + (tdat.mfo.max() - tdat.mfo.min()))/12
    
    #%% Calculate statistics  
    trm = ['year','month','mfo']
    tavg_cols = ['LitLoad', 'SoilMoist',
       'VegLoad', 'RelDef', 'PET', 'ET', 'TRANS', 'UnderPET', 'UnderET',
       'PSlope', 'PDef', 'PLoad', 'PWind']
    #tsum_cols = ['SpreadIter']
    t90th_cols = ['LitLoad', 'SoilMoist',
       'VegLoad', 'RelDef', 'PET', 'ET', 'TRANS', 'UnderPET', 'UnderET',
       'PSlope', 'PDef', 'PLoad', 'PWind']
    
    tgrp = ['syr', 'mod', 'typ']
    tdat = tdat.assign(syr=syr_data
        ).assign(mod=mod_data
        ).assign(typ=typ_data
        )
                
    #%% Average Statistics
    tavg = tdat[tgrp + tavg_cols].groupby(tgrp
        ).mean(
        ).reset_index(drop=False)
    
    tavg.columns = tgrp + ["avg_" + item for item in tavg_cols]
            
    #%% 90th percetnile statistics
    t90th = tdat[tgrp + t90th_cols].groupby(tgrp
        ).quantile([.9]
        ).reset_index(drop=False)        
    
    t90th = t90th.drop(t90th.columns[3], axis=1)
    t90th.columns = tgrp + ["90th_" + item for item in t90th_cols]
    
    #%% Merge columns
    tstat = pd.merge(tavg,t90th,how='left')
    
    # Calculate nfire, fri, and nfr ['SpreadIter', 'SpreadProp']    
    tfires = tdat[tdat['SpreadIter'] > thresh][['mfo','SpreadIter']].sort_values
    tfires = tdat[tdat['SpreadIter'] > thresh][['mfo','SpreadIter']].sort_values(by=['mfo'])
    tstat['aburn'] = tfires['SpreadIter'].sum()    
    tstat['fri'] = tfires['mfo'].diff(1).mean()/12
    tstat['nfire'] = tfires.shape[0]
    tstat['nfr'] = (tyrs*barea)/tstat.aburn #sum_SpreadIter.values
    tstat['50th_fsz'] = tfires['SpreadIter'].quantile(0.5)
    tstat['90th_fsz'] = tfires['SpreadIter'].quantile(0.9)
    tstat['avg_fsz'] = tfires['SpreadIter'].mean()
    tstat['max_fsz'] = tfires['SpreadIter'].max()
    
    tstat['i0'] = i0
    tstat['i1'] = i1
    tstat['wmfire_seed'] = wmfire_seed    
    dat.append(tstat)        
    
    
dat = pd.concat(dat)

#%% Write to tsv
pathlib.Path(outdir_data).mkdir(parents=True, exist_ok=True)
outfile=f"{syr_data}_{mod_data}_{typ_data}_analysis_WMFireGridTable.csv"
outfile = os.path.join(outdir_data,outfile) 
dat.to_csv(outfile, index=False)
