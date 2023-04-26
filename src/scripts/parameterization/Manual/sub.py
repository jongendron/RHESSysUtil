import os, sys
import pandas as pd
import numpy as np

#print(sys.argv)

file = sys.argv[1]
new_in_path = '"' + sys.argv[2] + '"'
new_out_path = os.path.join(sys.argv[3],sys.argv[4])
new_out_path = '"' + new_out_path + '"'
print(new_in_path)
print(new_out_path)

varlist = '"' + sys.argv[5] + '"'

# load table
tbl = pd.read_csv(file, comment="#")
nr = np.arange(0,tbl.shape[0])
nc = np.arange(0,tbl.shape[1])

# find row and column
cidx = nc[(tbl.columns == 'value')] # value column index
ridx1 = nr[(tbl['variable'] == '"in_path"')] # in_path column index
ridx2 = nr[(tbl['variable'] == '"out_path"')] # out_path column index
ridx3 = nr[(tbl['variable'] == '"varlist"')] # varlist column index
ridx4 = nr[(tbl['variable'] == '"extract_write"')] # don't keep extract files
print(f"cidx: {cidx}\nridx1: {ridx1}\nridx2: {ridx2}")

# replace
#tbl.iloc[(ridx,cidx)] = subvalue
tbl.iloc[(ridx1,cidx)] = new_in_path
tbl.iloc[(ridx2,cidx)] = new_out_path
tbl.iloc[(ridx3,cidx)] = varlist
tbl.iloc[(ridx4,cidx)] = '"False"'

#print(tbl.iloc[(ridx2, cidx)])
#print(tbl)

# write
tbl.to_csv("progset_tmp.csv", index_label=False, index=False)

