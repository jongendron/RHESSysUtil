import sys, os, pathlib
import numpy as np
import pandas as pd

#%% Program Settings / variables

#%% Command Line Argumenets
print(sys.argv)
file_data = sys.argv[1]
outdir_data=sys.argv[2]
syr_data=sys.argv[3]
mod_data=sys.argv[4]
typ_data=sys.argv[5]

# cols to groupby
idx_cols = ['patchID']
idx_cols = ['syr', 'mod', 'typ'] + idx_cols

#%% Prepare data
lfile_data = pd.read_csv(file_data, delim_whitespace=True)
lfile_data.columns = ['i0', 'i1', 'file']

#%% Start looping through file in chunks
print("Extracting Spatial data get getting running average")
print("\n\n")

for i in range(0,len(lfile_data)):
    print(f"Iteration: {i+1} of {len(lfile_data)}")
    tdat = pd.read_csv(lfile_data.file[i])    
    cnt = tdat.groupby(idx_cols).size().rename('n').reset_index(drop=False)       
    tdat = tdat.groupby(idx_cols).sum().reset_index(drop=False)
    tdat = pd.merge(tdat,cnt, on=idx_cols, how='left')
    #print(tdat,"\n\n")
    
    # Appending working df
    if i == 0:
        dat = tdat
    else:
        dat = pd.concat([dat,tdat],axis=0) # bind rows to working df        
        dat = dat.groupby(idx_cols).sum().reset_index(drop=False) # groupby then sum up colum values
        
    print(dat,"\n\n")

# Get the average of final df
idx2_cols = idx_cols + ['n']
dat_cols = [item for item in dat.columns if item not in idx2_cols]
dat.loc[:,dat_cols] = dat.loc[:,dat_cols].div(dat.n, axis=0).round(3)

# Write to file
print("Writing Temporal inter-simulation average Data to File")
pathlib.Path(outdir_data).mkdir(parents=True, exist_ok=True)
outfile=f"{syr_data}-{mod_data}-{typ_data}_avg-time-avg_WMFireGridTable.csv"
outfile = os.path.join(outdir_data,outfile) 
dat.to_csv(outfile, index=False)