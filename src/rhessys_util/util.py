# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 15:53:17 2022

@author: jonge
"""

import os, sys
import numpy as np
import pandas as pd

#%% Count number of none blank lines in a file
def count_line(File: str) -> int:
    """
    Counts the number of none blank lines in a file. Intended for csv or tsv format
    files.

    Parameters
    ----------
    File : str
        Path to the file to be read.

    Returns
    -------
    int
        Total number of lines in file that contain more than just whitespace.

    """
    
    count = 0
    with open(File) as fp:
        for line in fp:
            if line.strip():
                count += 1
    return count