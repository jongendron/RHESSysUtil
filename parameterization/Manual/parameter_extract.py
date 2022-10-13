# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 16:22:18 2022

@author: PETBUser
"""

#%% Load Dependecnies
import sys
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

addpath = os.path.abspath('../../') # RHESSyUtil
sys.path.insert(1, addpath)
import functions_analysis as rh


%matplotlib inline
#%% 1) Gather list of RHESSys output files to analyze
fpath = "./input/patch-basin-hydrcal-1"
filelist = rh.create_filelist(Path=fpath, Delim="_", ID_loc=[0, 1], inc_patn=["patch.yearly"], ex_patn=["grow"])

#%% 2) Gather a list of RHESSys parameter set files and create parameter data.table
fpath = "./input/patch-basin-hydrcal-1"
parlist = rh.create_filelist(Path=fpath, Delim="_", ID_loc=[], inc_patn=["parlist.txt"], ex_patn=[])
parlist = parlist.reset_index(drop=True)

partbl = []
for file in parlist['file']:
    partbl.append(pd.read_csv(file, sep="\t"))

partbl = pd.concat(partbl)


#%% 3) Extract Data from RHESSys output files for each setfile
dat = []
unq_idx = filelist.i0.unique()
vlist = ['soilc', 'plantc', 'litrc']
#vlist = ['soilc', 'plantc']

for idx in unq_idx:
    flist = filelist[filelist.i0 == str(idx)]
    dtmp = rh.merge_sims(Filelist=flist['file'], Varlist=vlist, Spat='patch', Time='yearly')    
    dat.append(dtmp)

#%% 
print()
for i in range(0,len(dat)):
    print(f"[{i}]\n")
    for j in range(0,len(vlist)):        
        print(f"[{vlist[j]}]\n")
        #print("[{}]\n\n".format(vlist[j]))
        print(dat[i][j],'\n\n')

#%% Plot some variables

dtmp = dat[0][0].copy()
dtmp['syr'] = np.arange(0,dtmp.shape[0])
dtmp = dtmp.iloc[:,np.append(-1,np.arange(2,dtmp.shape[1]-1))]

#%% Plot Seaborn
#plt.show()
#dtmp2 = dtmp.copy().set_index('syr')
#sns.relplot(data=dtmp2, kind='line', marker='', legend="")

#vlist[2]

#%% Pivot/melt

#dtmp3 = pd.pivot(dtmp2.copy(), index=[])
colnames = list(dtmp.columns)[1:]
dtmp3 = pd.melt(dtmp.copy(), id_vars=['syr'], value_vars=colnames, var_name="Set", value_name="value")

cvt_dict = {'Set' : float}

dtmp3 = dtmp3.astype(cvt_dict)
dtmp4 = dtmp3.groupby('Set')
soilc = dtmp4[['value']].mean()

norm = plt.Normalize(soilc.min(), soilc.max())
sm = plt.cm.ScalarMappable(cmap="Reds", norm=norm)
sm.set_array([])

#%% 
ax = sns.lineplot(data=dtmp3, x='syr', y='value', hue="Set", palette='Reds')
ax.get_legend().remove()
ax.figure.colorbar(sm)
plt.show()

#%% Plot this now 



ax = sns.lineplot(data=dtmp3, x="syr", y="value", cbar="Set")
