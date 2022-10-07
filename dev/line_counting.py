# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import pandas as pd

flist = os.listdir()

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

#%% Counting none blank lines (BING)

for file in flist:
    print(file,end="; ")
    print('None-blank lines:', count_line(file))

#%% Looping (counts blank lines though)
for file in flist:
    print(file)
    with open(file) as fp:
        for count, line in enumerate(fp):
            # print(f"\tCount: {count}; Line: {line}",sep="")
            pass
    print('Total Lines', count + 1)
    print()
    
#%% Generator
def _count_generator(reader):
    b = reader(1024 * 1024)
    while b:
        yield b
        b = reader(1024 * 1024)

#%% Apply Generator test

for file in flist:
    print(file,end="; ")
    with open(file, 'rb') as fp:
        c_generator = _count_generator(fp.raw.read)
        # count each \n
        count = sum(buffer.count(b'\n') for buffer in c_generator)
        print('Total lines:', count + 1)

#%% Read only certain rows of a file

fl = flist[6]

# Index rows starting with 0 ->
# NR to skip = row index if header is read

#%% 
# With Header
# nr = count_line(fl) - 1
bnd = [0,2]
st = bnd[0]
end = bnd[1] - bnd[0] + 1
print(pd.read_csv(fl, sep="\t", header = None, skiprows=st, nrows=end))

#%% With no upper bound
bnd = [2,4]
st = bnd[0]
end = bnd[1] - bnd[0] + 1
# end = None
pd.read_csv(fl, sep="\t", header=None, skiprows=1)
# print(pd.read_csv(fl, sep="\t", header=None))

#%% 
# Without Header
# nr = count_line(fl)
bnd = [0,2]
st = bnd[0]
end = bnd[1] - bnd[0] + 1
print(pd.read_csv(fl, sep="\t", header = None, skiprows=st, nrows=end))
# print(pd.read_csv(fl, sep="\t", header=None))


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



