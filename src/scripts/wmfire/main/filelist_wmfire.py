# Imports
import sys, os, pathlib
import numpy as np
import pandas as pd
inc_dir = os.path.abspath("/data/adam/jonathan.gendron/rhessys/RHESSysUtil/src/rhessys_util") # path of rhessys_util
# inc_dir = r"{}".format(inc_dir)
sys.path.append(inc_dir)
from util import filelist as fl

# # Program Settings
# sys.argv = [
# 	sys.argv[0],
# 	"/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/1900/nohs/brw",
# 	"/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/1900/nohs/brw/storage",
# 	1900,
# 	"nohs",
# 	"hist"
# ]

indir = sys.argv[1]
outdir = sys.argv[2]
syr = sys.argv[3]
mod = sys.argv[4]
typ = sys.argv[5]

#%% Create the filelist
datlist = fl(Path=indir, Delim="_", ID_loc=[0,1], inc_patn=['WMFireGridTable'], ex_patn=[None])

#%% Create parfile list
parlist = fl(Path=indir, Delim="_", ID_loc=[0,1], inc_patn=['parlist'], ex_patn=[None]).rename(columns={"file" : "parfile"})

#%% Merge the two
datlist = pd.merge(datlist, parlist, how="left", on=['i0', 'i1'], sort=False)
wmfire_seed = np.empty(datlist.shape[0])

#%% Extract the FireID parameters
for i in range(0,datlist.shape[0]):	
	wmfire_seed[i] = pd.read_csv(datlist['parfile'][i], delim_whitespace=True)['wmfire_seed'][0]
	
datlist['wmfire_seed'] = wmfire_seed.astype(int)

#%% Write to tsv
pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
#outfile = os.path.join(outdir,"wmfire_filelist.txt")
outfile = os.path.join(outdir,f"{syr}-{mod}-{typ}_wmfire_filelist.txt") 
datlist.to_csv(outfile, index=False, sep="\t")
