import functions_parameter_creation as pc
import pandas as pd
import numpy as np
import os

vnames = ['m', 'k', 'po', 'pa', 'gw1', 'gw2']
vconst = [1, 1, 1, 1, 0.1, 0.1]
vmin = [0.5, 1, 0.5, 0.5, 0.01, 0.01]
vmax = [1.5, 10, 2.0, 2.0, 0.25, 0.25]
vsd = [0.10, 0.10, 0.10, 0.10, 0.05, 0.05]
vmethod = ['seq', 'seq', 'seq', 'seq', 'seq', 'seq']
vlength = 100
vwrite = True
voutfile_path = "."
voutfile_name = "set1"
voutfile_type = "tsv"

# Single Set
#pc.param_create(Names=vnames,                                                                                                                                                                                                                        Const=vconst, Min=vmin, Max=vmax, Sd=vsd,                                                                                                                                                                                                    Method=vmethod, Length=vlength, Write=vwrite,                                                                                                                                                                                                Outfile_path=voutfile_path, Outfile_name=voutfile_name,                                                                                                                                                                                      Outfile_type=voutfile_type)  

# Sensitivity sets
voutfile_path = 'sets/patch_basin_cal/cal1'
smethod = ['const']*len(vnames)

for i in range(0,len(vnames)):
	vmethod = smethod.copy()
	vmethod[i] = 'seq'
	voutfile_name = 'set' + str(i+1)	

	pc.param_create(Names=vnames, 
		Const=vconst, Min=vmin, Max=vmax, Sd=vsd, 
		Method=vmethod, Length=vlength, Write=vwrite, 
		Outfile_path=voutfile_path, Outfile_name=voutfile_name, 
		Outfile_type=voutfile_type)

	print()


