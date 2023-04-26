import sys, os, pathlib
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil import relativedelta

print(sys.argv)
#%% Program settings
tag_data = sys.argv[1]
#file_data = "1_1_fire-brw-2075-CSIRO-rcp85-1_WMFireGridTable.csv"
file_data = sys.argv[2]
#file_idx = "/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire/BRW_col-row-patchID.csv"
file_idx = sys.argv[3]
outdir_data=sys.argv[4]
#chk_size = 27871*5 # 27871 = number of patches | 5 = number of months outputted / yr (fire season)
chk_size = 27871*20 # 27871 = number of patches | 5 = number of months outputted / yr (fire season)
idx_merge = False
spat_avg = True
orig = datetime.strptime('1900-01-01', "%Y-%m-%d")

#%% Prepare auxillary data
hdr = pd.read_csv(file_data, nrows=1, header=None).to_numpy()[0,].tolist()
idx = pd.read_csv(file_idx)

#%% Start looping through file in chunks
#nchk = 0
i = 1
dat = [] # empty list

print("\n\n\n")

for chunk in pd.read_csv(file_data, chunksize=chk_size, skiprows=1, header=None, names=hdr):    
    print(f"Chunk: {i}\n")
    
    if idx_merge == True:
        chunk = pd.merge(chunk, idx, on=['col','row'], how='left', sort=False)
        
    chunk.replace([-1], np.nan, inplace=True)
    chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
    chunk.loc[chunk['SpreadIter'] > 0, 'SpreadIter'] = 1    
    chunk.loc[chunk['FailedIter'] > 0, 'FailedIter'] = 1
    chunk.loc[chunk.RelDef<0.001, 'RelDef'] = np.nan
    
    #chunk.loc[chunk['SpreadIter'] <= 0, 'SpreadIter'] = 0
    #chunk.loc[chunk['SpreadIter'] > 0, 'SpreadIter'] = 1    
    #chunk.loc[chunk['FailedIter'] <= 0, 'FailedIter'] = 0
    #chunk.loc[chunk['FailedIter'] > 0, 'FailedIter'] = 1
    #chunk.replace([np.inf, -np.inf], np.nan, inplace=True)    
    #col_psp = ['PSlope', 'PDef', 'PLoad', 'PWind']
    #chunk[col_psp] = chunk[col_psp].replace(-1, np.nan)
    
    
    print("\n\n\n")
    print(chunk)
    print("\n\n\n")
    
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
             
    chunk['datetime'] = chunk[['year','month']].apply(lambda x: datetime.strptime('-'.join(x.values.astype(str)), "%Y-%m"), axis="columns")
    chunk['mfo'] = chunk['datetime'].apply(lambda x: relativedelta.relativedelta(x, orig).years*12 + relativedelta.relativedelta(x, orig).months)
    del chunk['datetime']
    
    dat.append(chunk)
    i += 1    
    print("\n\n\n")       

dat = pd.concat(dat)

#%% Write to tsv
pathlib.Path(outdir_data).mkdir(parents=True, exist_ok=True)
outfile=tag_data + "_tidy_WMFireGridTable.csv"
outfile = os.path.join(outdir_data,outfile) 
dat.to_csv(outfile, index=False)
