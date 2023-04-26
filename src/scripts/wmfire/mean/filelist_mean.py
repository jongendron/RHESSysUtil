#%% Imports
import sys, os, pathlib
inc_dir = os.path.abspath("/data/adam/jonathan.gendron/rhessys/RHESSysUtil/src/rhessys_util") # path of rhessys_util
inc_dir = r"{}".format(inc_dir)
sys.path.append(inc_dir)
import numpy as np
import pandas as pd
from util import filelist as fl

#%% Program Settings
indir = sys.argv[1]
outdir = sys.argv[2]
syr = sys.argv[3]
mod = sys.argv[4]
typ = sys.argv[5]

#%% Create the filelist
datlist = fl(Path=indir, Delim="_", ID_loc=[0,1], inc_patn=['WMFireGridTable',syr,mod], ex_patn=[None])
#datlist = fl(Path=indir, Delim="_", ID_loc=[0,1], inc_patn=['spat_fri',syr,mod], ex_patn=[None])

#%% Write to tsv
pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
outfile = os.path.join(outdir,f"{syr}-{mod}-{typ}_wmfire_filelist.txt") 
datlist.to_csv(outfile, index=False, sep="\t")
