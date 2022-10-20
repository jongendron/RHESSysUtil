#!/usr/bin/env conda run -n Python_3.10.0_v1
# -*- coding: utf-8 -*-
###### #!/usr/bin/env Python3
###### -*- coding: utf-8 -*-

"""
Created on June 1 2022
Calculate model performance on NPP/GPP ratio
@author: liuming
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys 
import os
from os.path import exists
import math
import scipy.stats

#from scipy.interpolate import make_interp_spline, BSpline
#from scipy.ndimage.filters import gaussian_filter1d

if len(sys.argv) <= 1:
    print("Usage:" + sys.argv[0] + "<growth_year_file> <valid_start_year> <valid_end_year> <valid_veg_id> <target1> <target_stddev1> ... <outdist_file>\n")
    sys.exit(0)
    
#target0:AGBc (kgC/m2)
#target1:height (m)
    
#numtargets =  int((len(sys.argv) - 6) / 2)
#numtargets =  int((len(sys.argv) - 7) / 2)
numtargets =  int((len(sys.argv) - 8) / 2)
print("numtargets :" + str(numtargets))   
print("sys.argv:",sys.argv)
 
growth_year = sys.argv[1] 
#"/home/liuming/mnt/hydronas2/Projects/FireEarth/Cedar/Outputs/spinup_fire__grow_stratum.yearly"
valid_start_year = int(sys.argv[2]) 
# = 1990
valid_end_year = int(sys.argv[3]) 
# = 2018
valid_veg_id = int(sys.argv[4]) 
# = 1
target = dict()
target_stddev = dict()

for t in range(numtargets):
    idx = 5 + t * 2
    target[t] = float(sys.argv[idx]) 
    target_stddev[t] = float(sys.argv[idx+1])
    #print("targets :" + str(t) + " target:" + str(target[t]) + " std_dev:" + str(target_stddev[t]))   
    
# = 0.5
outdist = sys.argv[len(sys.argv)-1] 
likefile = sys.argv[len(sys.argv)-2]
avgfile = sys.argv[len(sys.argv)-3]
idx = sys.argv[len(sys.argv)-4]

patch_stata_veg = "/home/jon/rhessys/tools/parameterization/patch_basin_strata.csv"

patch_strata = pd.read_csv(patch_stata_veg,delimiter=",",header=0)
growth = pd.read_csv(growth_year,delimiter=" ",header=0)
growth['gpp'] = growth['psn_net'] + growth['mr'] + growth['gr']
growth['npp_gpp_ratio'] = growth['psn_net'] / growth['gpp']

growth = pd.merge(growth, patch_strata, left_on=  ['patchID', 'stratumID'],right_on= ['patch_ID', 'canopy_strata_ID'], how = 'left')

avg = dict()
dist = dict()
tdist = 1.0
for t in range(numtargets):
    # It looks like we are using the mean of model data for a particlar time range to inform the data-likelihood function
    # Why are we not considering the error between model and observed to do this?
    # Ex: norm(target[t] - avg[t],0,(0.3target[t])^2), which is guassian propbability distribution suggested from the Paper
    # Update: apparently norm(target[t] - avg[t]; mu = 0, sd = (0.3*target[t])^2) == norm(avg[t]; mu = target[t], sd = (0.3*target[t])^2) (both equal same thing so this is valid approach
    if t == 0:
        #avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['npp_gpp_ratio'].mean()
        avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['AGBc'].mean()
    elif t == 1:
        avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['height'].mean()
    elif t == 2:
        #avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['psn_net'].mean()
        avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['LAI'].mean()
    elif t == 3:
        #avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['proj_lai'].mean()
        #avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['LAI'].mean()
        #avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['height'].mean()
        avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['psn_net'].mean()
    else:
        avg[t] = growth[(growth['veg_parm_ID'] == valid_veg_id) & (growth['year'] >= valid_start_year) & (growth['year'] <= valid_end_year)]['npp_gpp_ratio'].mean()

    #likelyhood
    #mean ratio 0.5 95%:0.4-0.6    stddev=0.051
    
    dist[t] = scipy.stats.norm.pdf(avg[t],loc=target[t],scale=target_stddev[t])
    tdist = tdist * dist[t]
    #print("targets:" + str(t) + " avg:" + str(avg[t]) + " target_value:" + str(target[t]) + " std_dev:" + str(target_stddev[t]) + " dist:" + str(dist[t]) + " tdist:" + str(tdist))

print("idx: ",idx)
print("avg:",avg)
print("target:",target)
print("dist:",dist)
print("tdist:",tdist)
tdist = round(tdist,6)
if tdist == 0:
    tdist = 0.000001
    print("corrected tdist:",tdist) # minimal value it can take on for this program

with open(outdist, 'w') as fh:
    fh.write(str('%.12f' % tdist) + '\n')

with open(likefile, 'w') as fl1:
    fl1.write(str("%.12s\t" % idx))
    for key in dist.keys():
        fl1.write(str("%.12f\t" % dist[key]))
    fl1.write(str('\n'))

with open(avgfile, 'w') as fl2:
    fl2.write(str("%.12s\t" % idx))
    for key in avg.keys():
        fl2.write(str("%.12f\t" % avg[key]))
    fl2.write(str('\n'))


