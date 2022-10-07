# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 12:28:35 2022

@author: PETBUser
"""

#%% Function to add group index number to all rows of dataframe (FAILED)

def format_grpidx(Dataframe: pd.DataFrame, Groups: list, ID: str) -> pd.DataFrame:
    """
    Using the groups specified in `Groups`, add the corresponding group number
    to each row of the dataframe `Dataframe`.
    
    *Used in format_simtime() function as means of calculation*
    
    *Does not sort dataframe by date, so groups #s reflect the order in which
    groups appear (from top row to bottom row)*

    Parameters
    ----------
    Dataframe : pd.DataFrame
        Pandas DataFrame to be modified with group #s
    Groups : list
        Columns in `Dataframe` to groupby and then count group numbers.

    Returns
    -------
    Modified version of `Dataframe` with group nubers according to `Groups`

    """    
      
    ## Check if input arguements are valid ##
    
    hdr = Dataframe.columns
    
    if type(Groups).__name__ != 'list':
        print("Error: `Groups` is not a list.")
        return
    
    if len(Groups) < 1:
        print("Error: Must group by at least one valid column.")
        return
        
    ltest = [item in hdr for item in Groups]
    if not all(ltest):
        print("Error: `Group` choice, {} is not valid."
              .format(np.array(Groups)[ltest]))
        return    
    
    if type(ID).__name__ != 'str':
        print("Error: `ID` is not a string.")
        return
    
    if len(ID) < 1:
        print("Error: `ID` must be at least one character long")
        return
    
    # Create Groups
    dftmp = Dataframe.copy()
    dftmp[ID] = 0
        
    grps = dftmp.groupby(by=Groups, sort=False, as_index=False).groups # i.e ['syr', 'month'] # Set sort to false so it donesn't arrange groups alphanumerically
    kys = grps.keys()      
    

    i = 0 # starts at group 0
    
    # Alter the dataframe
    for ky in kys:
        i += 1 # group number
        idx = grps[ky]
        dftmp.iloc[idx,-1] = i # set all rows in the last column equal to i
    
    # dftmp[ID].max() - dtmp[ID].min() # number of smths
    
    return dftmp

# 1. check if this workflow aggregates to same values as R workflow
# 2. check if this exact function names groups on first come first serve
# basis, or if it sort by alphabetical / numerical order (a-z or lowest - highest)

#%% Attempt to extract group numbers from groupby function in pandas

# works here but not in the function
# sort=F will not sort when you perform a function
# but it does sort the keys
df1 = pd.DataFrame(dict1)
df1.groupby(['a'], sort=True, as_index=False).count() 
df1.groupby(['a'], sort=False, as_index=False).count()

# and it does not change the keys! so be sure to use both sort=False and as_index=False
# to preserve the order of data when group keys are named
df1 = pd.DataFrame(dict1)
df1.groupby(['a'], sort=True, as_index=False).groups
df1.groupby(['a'], sort=False, as_index=False).groups
tmp = df1.groupby(['a'], sort=False, as_index=False).groups

for ky in tmp:
    print(ky)


# df2 = pd.DataFrame([[1980, 1980, 1980, 1980, 1970, 1970, 1970, 1970],[3, 7, 10, 11, 1, 5, 6, 10]], , columns=['a', 'b'])


