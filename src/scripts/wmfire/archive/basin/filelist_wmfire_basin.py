#%% Imports
import sys, os, pathlib
inc_dir = os.path.abspath("/data/adam/jonathan.gendron/rhessys/RHESSysUtil/src/rhessys_util") # path of rhessys_util
inc_dir = r"{}".format(inc_dir)
sys.path.append(inc_dir)
import numpy as np
import pandas as pd
from util import filelist as fl

print(sys.argv)
#%% Program Settings
indir = sys.argv[1]
#outdir = indir
outdir = sys.argv[2]

#%% Create the filelist
datlist = fl(Path=indir, Delim="_", ID_loc=[0,1,2], inc_patn=['tidy_WMFireGridTable'], ex_patn=[None])

#%% Write to tsv
outfile = os.path.join(outdir,"wmfire_basin_filelist.txt") 
datlist.to_csv(outfile, index=False, sep="\t")
