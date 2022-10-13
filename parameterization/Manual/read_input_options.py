# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 15:08:59 2022

@author: jonge
"""

#%%
import numpy as np
import pandas as pd

#%%
df1 = pd.read_csv('./Input_settings.txt', comment='#')

print()
for col in df1.columns:    
    print(f"[{col}]")
    print(df1[col])
    print()
    
#%%
for var, func, cl, val in df1[['Variable','Function', 'Class', 'Value']].values:
    var2 = var.replace('\"', '').replace(' ', '').split(',')[0]
    func2 = var.replace('\"', '').replace(' ', '').split(',')[0]
    cl2 = cl.replace('\"', '').replace(' ', '').split(',')[0]
    val2 = val.replace('\"', '').replace(' ', '').split(',')
    
    if cl2 != 'list':
        val2 = ' '.join(val2)
        
    #print(f"{cl2}; {type(cl2)}; val2")
    print(f"{cl2}; {val2}")
        
    
    
    
    
    
