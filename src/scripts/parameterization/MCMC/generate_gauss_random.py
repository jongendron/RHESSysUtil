#!/usr/bin/env conda run -n Python_3.10.0_v1
# -*- coding: utf-8 -*-
### #!/usr/bin/env python3
### # -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 20:40:56 2022

@author: liuming
"""

#import numpy as np
#import pandas as pd
import sys
import random

if len(sys.argv) <= 1:
    print("Usage:" + sys.argv[0] + "<mean> <stddev> <out_file>\n")
    sys.exit(0)

#print("""sys.argv[0]: {0}\n\
#sys.argv[1]: {1}\n\
#sys.argv[2]: {2}\n\
#sys.argv[3]: {3}\n"""
#        .format(sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3])
#        )

target = float(sys.argv[1])
stddev = float(sys.argv[2])
# = 0.5
outdist = sys.argv[3]

dist = random.gauss(target, stddev)

with open(outdist, 'w') as fh:
    fh.write(str('%.6f' % dist) + '\n')

