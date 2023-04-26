import sys, os, pathlib
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import relativedelta

#%% Program Settings / variables
idx_merge = False
spat_avg = True
analysis = True
orig = datetime.strptime('1900-01-01', "%Y-%m-%d")
thresh = 60   # 60 patches (ha)
barea = 27871 # 27871 patches (ha) in basin

#%% Command Line Argumenets
print(sys.argv)
file_data = sys.argv[1]
file_idx = sys.argv[2]
outdir_data=sys.argv[3]
syr_data=sys.argv[4]
mod_data=sys.argv[5]
typ_data=sys.argv[6]
i0_data =sys.argv[7]
i1_data =sys.argv[8]
wmfire_seed_data =sys.argv[9]

#%% Prepare data
idx = pd.read_csv(file_idx)
dat = pd.read_csv(file_data)

#%% Tidy the data
if idx_merge == True:
    dat = pd.merge(dat, idx, on=['col','row'], how='left', sort=False)
    
dat.replace([-1], np.nan, inplace=True)
dat.replace([np.inf, -np.inf], np.nan, inplace=True)
dat.loc[dat['SpreadIter'] > 0, 'SpreadIter'] = 1    
dat.loc[dat['FailedIter'] > 0, 'FailedIter'] = 1
dat.loc[dat.RelDef<0.001, 'RelDef'] = np.nan

if spat_avg == True:
    dat = dat.groupby(['year','month']
        ).agg({'SpreadIter' : 'sum',
            'FailedIter' :	'sum',
            'SpreadProp' :	'mean',
            'LitLoad' : 'mean',	
            'SoilMoist' : 'mean',	
            'VegLoad' :  'mean',
            'RelDef' :  'mean',	
            'PET' :  'mean',	
            'ET' :  'mean',
            'TRANS' :  'mean',	
            'UnderPET' :  'mean',	
            'UnderET' :  'mean',	
            'PSlope' :  'mean',	
            'PDef' :  'mean',	
            'PLoad' :  'mean',	
            'PWind' : 'mean'
            }
        ).reset_index(drop=False)                              
         
dat['datetime'] = dat[['year','month']].apply(lambda x: datetime.strptime('-'.join(x.values.astype(str)), "%Y-%m"), axis="columns")
dat['mfo'] = dat['datetime'].apply(lambda x: relativedelta.relativedelta(x, orig).years*12 + relativedelta.relativedelta(x, orig).months)
del dat['datetime']

print("\n\n\n")       
     
#%% Write tidy WMFire_table to csv
outdir = os.path.join(outdir_data,"tidy_WMFireGridTable")
pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

outfile=f"{syr_data}_{mod_data}_{typ_data}_tidy_WMFireGridTable.csv"
outfile = os.path.join(outdir,outfile) 
dat.to_csv(outfile, index=False)

###################################################
if analysis == True:    
    tyrs = (1 + (dat.mfo.max() - dat.mfo.min()))/12

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
    dat = dat.assign(syr=syr_data
        ).assign(mod=mod_data
        ).assign(typ=typ_data
        )
                
    #%% Average Statistics
    tavg = dat[tgrp + tavg_cols].groupby(tgrp
        ).mean(
        ).reset_index(drop=False)

    tavg.columns = tgrp + ["avg_" + item for item in tavg_cols]
            
    #%% 90th percetnile statistics
    t90th = dat[tgrp + t90th_cols].groupby(tgrp
        ).quantile([.9]
        ).reset_index(drop=False)        

    t90th = t90th.drop(t90th.columns[3], axis=1)
    t90th.columns = tgrp + ["90th_" + item for item in t90th_cols]

    #%% Merge columns
    tstat = pd.merge(tavg,t90th,how='left')

    # Calculate nfire, fri, and nfr ['SpreadIter', 'SpreadProp']    
    tfires = dat[dat['SpreadIter'] > thresh][['mfo','SpreadIter']].sort_values
    tfires = dat[dat['SpreadIter'] > thresh][['mfo','SpreadIter']].sort_values(by=['mfo'])
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
    
    #%% Write analysis WMFire_table to csv
    outdir = os.path.join(outdir_data,"analysis_WMFireGridTable")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    outfile=f"{syr_data}_{mod_data}_{typ_data}_analysis_WMFireGridTable.csv"
    outfile = os.path.join(outdir,outfile) 
    dat.to_csv(outfile, index=False)

    