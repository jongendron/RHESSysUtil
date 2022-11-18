#%% Imports
import sys, os
tar_dir1 = os.path.abspath(os.path.join(os.path.dirname(__file__))) # path of rhessys_util
tar_dir1 = r"{}".format(tar_dir1)
sys.path.append(tar_dir1)
import functions_parameter_creation as pc
import pandas as pd
import numpy as np
del tar_dir1

#%% Settings
vnames = ['m', 'k', 'po', 'pa', 'gw1', 'gw2']
vconst = [1000.0, 5.241, 0.622, 0.500, 0.20, 0.049]
vmin = [1.000, 1.000, 0.100, 0.100, 0.100, 0.050]
vmax = [1000.0, 1000.0, 2.000, 2.000, 0.500, 0.500]
vsd = [25.000, 25.000, 0.20, 0.20, 0.20, 0.10]
vmethod = ['seq', 'const', 'const', 'const', 'const', 'const']
vlength = 10
vwrite = True
voutfile_path = r"C:\Ubuntu\rhessys\RHESSysUtil\src\scripts\parameterization\Creation\sets\cal1"
voutfile_prefix = "set"
voutfile_type = "tsv"
voutfile_name = "set1"

#%% Sensitivity sets (all but one variable is constant)
#voutfile_path = 'sets/patch_basin_cal/cal1'
#smethod = ['const']*len(vnames)

for varidx in range(0,len(vnames)):
	method = ['const']*len(vnames)
	method[varidx] = 'seq'
	voutfile_name = voutfile_prefix + str(varidx+1)	

	pc.param_create(Names=vnames, 
		Const=vconst, Min=vmin, Max=vmax, Sd=vsd, 
		Method=method, Length=vlength, Write=vwrite, 
		Outfile_path=voutfile_path, Outfile_name=voutfile_name, 
		Outfile_type=voutfile_type)

	print()

