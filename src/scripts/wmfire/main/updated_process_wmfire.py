# Goals:
# 1. read *WMFire*.csv files chunkwise
# 2. perform spatial analysis (prob: SpreadIter (burn) | sum->avg: LitLoad, SoilMoist, VegLoad, RelDef, PET, ET, TRANS, UnderPET)
# 3. perform basin analysis
#   a. table of basin fire events greater than a threshold
#   b. dict containing stats for these events size, freq, density

# TODO: Do subshells initiated from SLURM jobs take on the correct Python virtual environment? Maybe I need to source it first?
import sys, os, pathlib
import numpy as np
import pandas as pd
import json

# Custom modules
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))  # Get the current directory of the script
sys.path.append(current_dir)  # Add the current directory to the sys.path
import wmfiretools as wmf  # Now you can import custom the module using a relative path
# from test2 import testvar

# Program Settings / variables
idx_merge = True

thresh = 809   # 60 patches future (ha) and 809 (ha) for historical
barea = 27871 # 27871 patches (ha) in basin
# chk_size = barea*20  # 20 = number of months outputted / yr (fire season), which 5 months*4
chk_size = barea*5  # 10 = number of months outputted / yr (fire season), which 5 months*1

# sys.argv = [sys.argv[0],
# # 	'/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/1900/nohs/brw/test.csv',
#     '/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/1900/nohs/brw/MeanMoIgn0p02-brw-1900-nohs-hist-1/1/8/1_8_MeanMoIgn0p02-brw-1900-nohs-hist-1_WMFireGridTable.csv',
# 	'/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire/BRW_col-row-patchID.csv',
# 	'/data/adam/jonathan.gendron/rhessys/Kamiak/output/test',
# 	1900,
# 	'hist',
# 	'nohs',
# 	1,
# 	1,
# 	100
# ]

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
i = 0
nchk = 0
current_syr = 0
current_smth = 0
datdict = dict()
datdict['fire'] = []

#TODO: Make sure these actually exist!
keep_time = ['syr', 'smth', 'month']
keep_fire = ['SpreadIter']
keep_eco = ['LitLoad', 'RelDef']  
#######################################

# bas_var = {}
datdict['basin'] = dict()
for item in keep_fire+keep_eco:
    datdict['basin'][item] = {
        'count': 0,
        'cumsum': 0,
        'mean': None
    }

datdict['spatial'] = {
    'coordinates': dict(),
    'variables': dict()
}

print("Extracting Data and Tidying\n\n")

for chunk in pd.read_csv(file_data, chunksize=chk_size, skiprows=1, header=None, names=hdr):
    i += 1
    print(f"\nChunk: {i}\n")

    if idx_merge == True:
        chunk = pd.merge(chunk, idx, on=['col','row'], how='left', sort=False)

    #tmp2 = chunk.copy()
    chunk.astype(float)  # make sure everything is float
    chunk.replace([-1], np.nan, inplace=True)
    chunk['SpreadIter'].replace(np.nan, 0, inplace=True)
    chunk.replace([np.inf, -np.inf], np.nan, inplace=True)
    chunk.loc[chunk['SpreadIter'] > 0, 'SpreadIter'] = 1 
    chunk.loc[chunk['FailedIter'] > 0, 'FailedIter'] = 1
    chunk.RelDef = chunk.RelDef.astype(float)
    chunk.loc[chunk.RelDef<0.001, 'RelDef'] = np.nan
    
    # print(chunk)
    #tmp3 = chunk.copy()

    # Add simtime  # TODO: Issues arrise when chunk size, barea and number of rows in file don't correspond correctly
    # Number of rows in file needs to be divisible by chunksize without remainder.
    current_syr += 1
    current_smth += 1
    try:
        chunk['syr'], chunk['smth'] = wmf.simtime(chunk, current_syr, current_smth, mth_size=barea, mth_per_yr=5)
        current_syr = chunk['syr'].max()
        current_smth = chunk['smth'].max()
    except ValueError as e:
        print(f'ValueError: {e}')
        print("Setting smth and syr to np.nan and keeping previous current_syr and current_smth.")
        chunk['syr'], chunk['smth'] = np.nan, np.nan

    # print(chunk)

    # TODO: Update Variable Tracker
    # Update the count
    for index, value in chunk[keep_fire + keep_eco].count().items():
        # print(index, value)
        datdict['basin'][index]['count'] += value

    # Update the cumsum
    for index, value in chunk[keep_fire + keep_eco].sum().items():
        # print(index, value)
        datdict['basin'][index]['cumsum'] += value

    for col, cnt, csum in [(col, datdict['basin'][col]['count'], datdict['basin'][col]['cumsum']) for col in keep_fire + keep_eco]:
        print(col, cnt, csum, sep=' | ')

    # TODO: Create basin scale fire table, filter by firesize threshold (thresh)
    chunk_copy = chunk.copy()
    btbl_fire = chunk_copy[keep_time + keep_fire].groupby(keep_time).sum().reset_index()  # TODO: Check if .groupby(sort=False) is needed
    btbl_fire = btbl_fire[btbl_fire['SpreadIter'] >= thresh]
    if not btbl_fire.empty:
        btbl_eco = chunk_copy[keep_time + keep_eco].groupby(keep_time).mean().reset_index()  # TODO: Check if .groupby(sort=False) is needed
        btbl = pd.merge(btbl_fire, btbl_eco, on=keep_time, how='left')
        # bas_fire.append(btbl)
        datdict['fire'].append(btbl)
        del btbl_eco
        
    del chunk_copy, btbl_fire

    # TODO: Spatial Data
    
    # First create dict of coordinates: {'x':[], 'y':[], 'patchID':[] or 'rowcol': []}
    chunk['rowcol'] = (chunk['row'].astype(str) + chunk['col'].astype(str)).astype(int)
    
    if idx_merge and 'patchID' in chunk.columns:  # sort by patchID
        # spat_coord = wmf.nest_dict_coord(spat_coord, chunk, patchID=True)
        datdict['spatial']['coordinates'] = wmf.nest_dict_coord(datdict['spatial']['coordinates'], chunk, patchID=True)
        grpby=['patchID']
    else:  # concat row & col -> rowcol (123 + 456 = 123456) then sort by rowcol
        # spat_coord = wmf.nest_dict_coord(spat_coord, chunk, patchID=False)
        datdict['spatial']['coordinates'] = wmf.nest_dict_coord(datdict['spatial']['coordinates'], chunk, patchID=False)
        grpby=['rowcol']
    
    # Second get the cnt and cumsum of each variable
    for var in (keep_fire +  keep_eco):
        # print()
        # print(var)
        datdict['spatial']['variables'] = wmf.nest_dict_stat(datdict['spatial']['variables'], chunk, var, groupby=grpby)


# Final Analysis

# datdict['fire'] = [pd.DataFrame({
# 'syr': [1, 100, 200, 300, 400, 500],
# 'smth': [1, 1200, 2400, 3600, 4800, 6000],
# 'SpreadIter': [5000, 20000, 17000, 27000, 15000, 25000],
# 'LitLoad': [0.8, 1.0, 0.95, 1.2, 0.9, 1.1],
# 'RelDef': [0.5, 0.8, 0.7, 0.9, 0.75, 0.85]}
# )]

print(f"\nFire table:\n{datdict['fire']}")
print()

# Basin Stats
# for var in bas_var:
for var in datdict['basin']:
    # bas_var[var][2] = bas_var[var][1]/bas_var[var][0] 
    # bas_var[var]['mean'] = bas_var[var]['cumsum']/bas_var[var]['count']
    datdict['basin'][var]['mean'] = datdict['basin'][var]['cumsum']/datdict['basin'][var]['count']
    # round
    datdict['basin'][var]['mean'] = round(datdict['basin'][var]['mean'], ndigits=3)
    datdict['basin'][var]['cumsum'] = round(datdict['basin'][var]['cumsum'], ndigits=3)

# Spatial Stats
# for var in spat_var:
for var in datdict['spatial']['variables']:
    # spat_var[var]['mean'] = spat_var[var]['cumsum']/spat_var[var]['count']
    datdict['spatial']['variables'][var]['mean'] = datdict['spatial']['variables'][var]['cumsum']/datdict['spatial']['variables'][var]['count']
    # round
    datdict['spatial']['variables'][var]['mean'] = np.round(datdict['spatial']['variables'][var]['mean'], decimals=3)
    datdict['spatial']['variables'][var]['cumsum'] = np.round(datdict['spatial']['variables'][var]['cumsum'], decimals=3)

# Basin Fire Table Stats
# Must have syr and smth to calculate FRI

if bool(datdict['fire']):
    datdict['fire'] = pd.concat(datdict['fire'], axis=0).reset_index(drop=True)  # drop index no need

    # Calculate fire stats (function)
    # TODO: Check that current_smth is the true number of months that have passed during sims
    # TODO: assumes file starts at smth 1 and that the last month is a fire season month
    # bas_fire = wmf.ftbl_stats(bas_fire, nyrs=current_smth/12, barea=barea, eco=True)
    datdict['fire'] = wmf.ftbl_stats(datdict['fire'], nyrs=current_smth/12, barea=barea, eco=True)

# Printing for debugging
print(f"\nFire:\n")
try:
    wmf.print_dict(datdict['fire'])
except:
    print(datdict['fire'])
print()

print(f"\nBasin:\n")
try:
    wmf.print_dict(datdict['basin'])
except:
    print(datdict['basin'])
print()

print(f"\nSpatial:\n")
try:
    wmf.print_dict(datdict['spatial'])
except:
    print(datdict['spatial'])
print()


# Writing to file (json format)
print("\nWriting to file", "\n")
outdir = os.path.join(outdir_data,"analysis_WMFire")
pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
outfile=f"{syr_data}_{mod_data}_{typ_data}_{i0_data}_{i1_data}_{wmfire_seed_data}_analysis_WMFire.json"
outfile = os.path.join(outdir,outfile)

# Convert ndarrays to list
wmf.convert_nested_ndarray(datdict)

#  Write dictionary to file
with open(outfile, "w") as file:
    # json.dump(datdict, file, indent=None)
    # json.dump(datdict, file, indent=2)
    tjson = wmf.tidy_json(datdict)
    file.write(tjson)

