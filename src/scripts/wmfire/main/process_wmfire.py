import sys, os, pathlib
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import relativedelta

#%% Program Settings / variables
idx_merge = True
spat_avg = False
analysis = True # False
spat_fri = False # True
spat_sum = True # False

orig = datetime.strptime('1900-01-01', "%Y-%m-%d")
##thresh = 809   # 60 patches (ha)
thresh = 60   # 60 patches (ha)
barea = 27871 # 27871 patches (ha) in basin
# chk_size = 27871*20 # 27871 = number of patches | 5 = number of months outputted / yr (fire season)
chk_size = barea*24  # 20 = number of months

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
hdr = pd.read_csv(file_data, nrows=1, header=None).to_numpy()[0,].tolist()
idx = pd.read_csv(file_idx)
idx_cols = [item for item in idx.columns if item not in ['col', 'row']]

#%% Start looping through file in chunks
i = 1
nchk = 0
dat = [] # empty list
print("Extracting Data and Tidying")
print("\n\n")

for chunk in pd.read_csv(file_data, chunksize=chk_size, skiprows=1, header=None, names=hdr):
    print(f"Chunk: {i}\n")
    print(chunk)
    #tmp1 = chunk.copy()

    if idx_merge == True:
        chunk = pd.merge(chunk, idx, on=['col','row'], how='left', sort=False)

    #tmp2 = chunk.copy()
    chunk.astype(float)  # make sure everything is float
    chunk.replace([-1], np.nan, inplace=True)
    chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
    chunk.loc[chunk['SpreadIter'] > 0, 'SpreadIter'] = 1 
    chunk.loc[chunk['FailedIter'] > 0, 'FailedIter'] = 1
    chunk.RelDef = chunk.RelDef.astype(float)
    chunk.loc[chunk.RelDef<0.001, 'RelDef'] = np.nan
    
    #tmp3 = chunk.copy()

    if spat_avg == True:
        chunk = chunk.groupby(['year','month']
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

    if spat_fri == True and idx_merge == True and spat_avg == False and spat_sum == False:
        chunk = chunk[chunk['SpreadIter'].notnull().values][idx_cols + ['year', 'month', 'SpreadIter']]  # only keep rows with a burn
        #tmp4=chunk.copy()
        if chunk.empty == False:
            nchk += 1
            chunk['datetime'] = chunk[['year','month']].apply(lambda x: datetime.strptime('-'.join(x.values.astype(str)), "%Y-%m"), axis="columns")
            chunk['mfo'] = chunk['datetime'].apply(lambda x: relativedelta.relativedelta(x, orig).years*12 + relativedelta.relativedelta(x, orig).months)
            del chunk['datetime']
            #dat.append(chunk)
            #tmp5=chunk.copy()
            #if i == 1:
            if nchk == 1:
                dat = chunk
            else:
                dat = pd.concat([dat,chunk],axis=0)            
        #print(chunk)
            #print("\n\n\n")
        i += 1        
        
    elif spat_sum == True and idx_merge == True and spat_avg == False and spat_fri == False:
        # group by idx_cols and get sum of each col and the count (# occurences)
        # chunk = chunk.drop(['year', 'month', 'col', 'row','SpreadIter', 'FailedIter', 'SpreadProp','PSlope', 'PDef', 'PLoad', 'PWind'], axis=1)
        chunk = chunk.drop(['year', 'month', 'col', 'row', 'FailedIter', 'SpreadProp','PSlope', 'PDef', 'PLoad', 'PWind'], axis=1)
        cnt = chunk.groupby(idx_cols).size().rename('n').reset_index(drop=False)
        chunk = chunk.groupby(idx_cols).sum().reset_index(drop=False)
        chunk = pd.merge(chunk,cnt, on=idx_cols, how='left')           
        # append dat
        if i == 1:
            dat = chunk
        else:
            dat = pd.concat([dat,chunk],axis=0)                    
            # group by idx_cols and get the sum of all cols (including the count)
            dat = dat.groupby(idx_cols).sum().reset_index(drop=False)        
        i += 1        
    else:               
        chunk['datetime'] = chunk[['year','month']].apply(lambda x: datetime.strptime('-'.join(x.values.astype(str)), "%Y-%m"), axis="columns")
        chunk['mfo'] = chunk['datetime'].apply(lambda x: relativedelta.relativedelta(x, orig).years*12 + relativedelta.relativedelta(x, orig).months)
        del chunk['datetime']
        #print(chunk)
        #print("\n\n\n")                
        #dat.append(chunk)
        if i == 1:
            dat = chunk
        else:
            dat = pd.concat([dat,chunk],axis=0)
        i += 1


#dat = pd.concat(dat)
# Final tidying
print("Final Tidying\n\n")
# Fix script, need to add step to set patches that had no fire to have fri == some value (250 year?, Inf?, 500 yrs?)
# This involves binding a df of 1 column with pachID wit the final df, and then setting NA's to Inf or some value
if spat_fri == True and idx_merge == True and spat_avg == False and spat_sum == False:  # TODO: This part doesn't work if data doesn't have syr and or smth outputed by RHESSys (assumes dates are not random)
    dat = dat.sort_values(idx_cols + ['mfo'])
    dat['fri'] = dat.groupby(idx_cols)['mfo'].diff(1)
    dat = dat[idx_cols + ['fri']].groupby(idx_cols).mean()/12
    dat = dat.reset_index(drop=False)
    dat['fri'] = dat['fri'].round(2)
    dat = dat[idx_cols + ['fri']]
elif spat_sum == True and idx_merge == True and spat_avg == False and spat_fri == False:
    idx2_cols = idx_cols + ['n']
    dat_cols = [item for item in dat.columns if item not in idx2_cols]
    dat.loc[:,dat_cols] = dat.loc[:,dat_cols].div(dat.n, axis=0).round(3)
    dat = dat.drop('n', axis=1)

dat = dat.assign(syr=syr_data
    ).assign(mod=mod_data
    ).assign(typ=typ_data
    )

print(dat, '\n\n')

# Writing to file   
#if spat_fri == True and spat_avg == False:
print("Writing to file", "\n\n")
if spat_fri == True and idx_merge == True and spat_avg == False and spat_sum == False:
    #%% Write spat fri WMFire_table to csv
    print("Writing Spatial Average FRI Data to File")
    outdir = os.path.join(outdir_data,"spat-fri_WMFireGridTable")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    outfile=f"{syr_data}_{mod_data}_{typ_data}_{i0_data}_{i1_data}_{wmfire_seed_data}_spat-fri_WMFireGridTable.csv"
    outfile = os.path.join(outdir,outfile) 
    dat.to_csv(outfile, index=False)
elif spat_sum == True and idx_merge == True and spat_avg == False and spat_fri == False:
    #%% Write spat WMFire_table to csv
    print("Writing Spatial Average WMFire Data to File")
    outdir = os.path.join(outdir_data,"time-avg_WMFireGridTable")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    outfile=f"{syr_data}_{mod_data}_{typ_data}_{i0_data}_{i1_data}_{wmfire_seed_data}_time-avg_WMFireGridTable.csv"
    outfile = os.path.join(outdir,outfile) 
    dat.to_csv(outfile, index=False)    
else:
    #%% Write tidy WMFire_table to csv
    print("Writing Spatial-Temporal average (Tidied) Data to File")
    outdir = os.path.join(outdir_data,"tidy_WMFireGridTable")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

    outfile=f"{syr_data}_{mod_data}_{typ_data}_{i0_data}_{i1_data}_{wmfire_seed_data}_tidy_WMFireGridTable.csv"
    outfile = os.path.join(outdir,outfile) 
    dat.to_csv(outfile, index=False)

######## Basin Average Fire Statistics ###########
if analysis == True and spat_fri == False:
    print("Analysing Tidied Data")    
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

    tstat['i0'] = i0_data
    tstat['i1'] = i1_data
    tstat['wmfire_seed'] = wmfire_seed_data
    
    #%% Write analysis WMFire_table to csv
    #outdir = os.path.join(outdir_data,"th809_analysis_WMFireGridTable")
    outdir = os.path.join(outdir_data,"analysis_WMFireGridTable")
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
            
    outfile=f"{syr_data}_{mod_data}_{typ_data}_{i0_data}_{i1_data}_{wmfire_seed_data}_analysis_WMFireGridTable.csv"
    outfile = os.path.join(outdir,outfile) 
    tstat.to_csv(outfile, index=False)

    