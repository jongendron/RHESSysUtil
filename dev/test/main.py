# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 12:13:22 2022

@author: jonge
"""
#%% Imports
import os, sys
CALL_DIR = os.path.dirname(__file__)
# UTIL_DIR = os.path.normpath(os.path.join(CALL_DIR, os.pardir, os.pardir, 'src'))
UTIL_DIR = os.path.abspath(os.path.join(CALL_DIR, os.pardir, os.pardir, 'src','rhessys_util'))
# os.listdir(UTIL_DIR)

#sys.path.insert(0, UTIL_DIR)
sys.path.append(UTIL_DIR)
print(sys.path)

# print(os.listdir(UTIL_DIR))


#%% 
import rhessys_util as rh

#%%



                  
                  

# DIR_RHESSYSUTIL = 
# FILEPATH = __file__
# FILENAME = os.path.basename(__file__)
# print(f"DIR: {DIR}\nFILEPATH: {FILEPATH}\nFILENAME: {FILENAME}")

# print()
# import lib.mod1 as mod1
# print()
# import lib.mod2 as mod2








