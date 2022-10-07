import pandas as pd
import numpy as np

likefile = "./likefile_test.txt"

dist = dict()
dist[0] = "hello"
dist[1] = "there"
dist[2] = "jon"

with open(likefile, 'w') as fl:
    for key in dist.keys():
        fl.write(str("%12s\t" % dist[key]))
    fl.write(str('\n'))


