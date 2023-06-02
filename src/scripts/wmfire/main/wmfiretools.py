import pandas as pd
import numpy as np
import json
from test2 import testvar

def skipseq(start, len: int=100, on_len: int=5, skip_len: int=7):
    """Generator Used with calculating simulation months when data is omitted from output.
    In the case of WMFire*csv files, only fire season months (6,7,8,9,10) are stored,
    when the model actually simulates months (1,2,3,4,5,6,7,8,9,10,11,12). Therefore, only
    5 out of 12 months are saved in the file, so when ordered simulation months we need to 
    count 5 on and skip 7.\n
        len [int]: length of the generator if converted to list.\n
        on_len [int]: length of sequence to preserve.\n
        skip_len [int]: length of sequence to skip.\n

    Sequence: list(range(start, start+on_len+1)) + list(range(start+on_len+1+skip_len, start+on_len+1+skip_len+on_len)) + ...
    """
    num = start
    seq_len = 0
    while True:
        if seq_len == len:
            break
        else:
            for i in range(on_len):
                if seq_len < len:
                    yield num
                    seq_len += 1
                    num += 1                    
                else:
                    break
            num += skip_len

def simtime(data: pd.DataFrame, start_syr: int, start_smth: int, mth_size: int, mth_per_yr: int) -> tuple:
    """returns tuple containing two arrays: (1) sim years and (2) sim months. Leverages skipseq for sim months.
    start [int]: starting.
    """
    nr = data.shape[0]
    yr_size = mth_size*mth_per_yr
    # num_yr = round(nr/yr_size)
    # num_mth = round(nr/mth_size)

    # TODO: Handle when file is not complete (number of rows is not divisible by mth_size and year_size)
    
    # 1. Get quotent and remainder (modulus) divmod(numerator, denomenator) for num_yr and num_mth  #TODO: Causes crash when chunk size is not multiple of number of years
    num_yr = divmod(nr,yr_size)
    if num_yr[1] > 0:
        raise ValueError('Error calculating syr, either\n(a) Number of rows per simulation year is invalid.\n(b)file is incomplete.\n(c)data is missing.')
    
    num_mth = divmod(nr,mth_size)
    if num_mth[1] > 0:
        raise ValueError('Error calculating smth, either\n(a) Number of rows per simulation month is invalid.\n(b)file is incomplete.\n(c)data is missing.')

    # 2. Calcluate syr and smth using the quotent
    # syr = np.arange(1, num_yr+1) + start_syr
    syr = np.arange(0, num_yr[0]) + start_syr
    syr = syr.repeat(yr_size)
    smth = list(skipseq(start_smth, len=num_mth[0], on_len=mth_per_yr, skip_len=(12-mth_per_yr)))
    smth = np.array(smth).repeat(mth_size)


    # TODO: 3. If there is a remainder (modulus), then perform ... T.B.D. ... This should only happen the file is cut short.
    # I think this should raise an exception because I don't know how to track position of syr and smth if this is not the last chunk
    # if num_yr[1] > 0:
    #     last_yr = syr[-1]  
    
    # if num_mth[1] > 0:
    #     last_smth = smth[-1]

    if len(syr) != len(smth):
        raise ValueError("Error calculating simulation time, len(syr) != len(smth).")  # TODO: Debug ValueError: Error with data.  ~iteration 4 
    
    return syr, smth


def nest_dict_coord(parent_dict: dict, data: pd.DataFrame, patchID: bool=False):
    """Extract the unique coordinates (row, col) and patchID (if available) from the WMFire Output\n
    and save them to parent_dict under parent_dict['coordinates']. Also checks for existance first.\n
        parent_dict [dict]: parent dictionary to add nested dictionary of data to.\n
        data [pd.DataFrame]: data to calculate count and sum from.\n
        patchID [bool]: if True, includes patchID as a column. If False, only includes rowcol (calculated).
    """
    # Check parent_dict exists
    if not isinstance(parent_dict, dict) or not isinstance(data, pd.DataFrame) or not isinstance(patchID, bool):
        raise TypeError('Either parent_dict, data, or patchID are not correct types.')  # TODO: Could make this a function itself and check each individually and raise error
    
    # Check that row and col exists
    if not bool(set(['row','col']) and set(data.columns)):
        raise ValueError('data does not contain fields `row` and `col`.')
    
    # Extract neccessary fields
    if patchID and 'patchID' in data.columns:
        fields = ['row', 'col', 'patchID']
        sort_fields = ['patchID']
    else:
        fields = ['row', 'col', 'rowcol']
        sort_fields = ['rowcol']
    
    # Store in the parent_dict
    # First check if they already exist
    ltest = True
    for field in fields:
        ltest = (ltest and 
        field in parent_dict and
        isinstance(parent_dict.get(field), np.ndarray))  # check if if it contains an np.array

    if not ltest:
        data_copy = data[fields].copy()

        # Remove duplicates
        data_copy = data_copy.drop_duplicates(keep='first')  # keep first occurences

        # Sort by sort_fields
        data_copy = data_copy.sort_values(by=sort_fields)

        # Populate the dictionary
        for x in fields:
            parent_dict[x] = data_copy[x].values

        # all(np.diff(parent_dict['patchID']) > 0)  # check that its numerically sorted
        # all(np.diff(parent_dict['rowcol']) > 0)  # check that its numerically sorted

    return parent_dict
    

def nest_dict_stat(parent_dict: dict, data: pd.DataFrame, variable: str, groupby: list):
    """Calculates the count and cumsum of `variable` in `data` grouped by `groupby`, then saves them to a subdictionary\n
    located in `parent_dict`. Intended for the use of calculating count and cumsum for each patchID (x,y combo) in WMFire\n
    tabular data.\n

        parent_dict [dict]: parent dictionary to add nested dictionary of data to.\n
        data [pd.DataFrame]: data to calculate count and sum from.\n
        variable [str]: variable to calculate count and sum for.\n
        groupby [list]: field(s) to group `data` by to calculate sum and count.\n
            Should be either patchID or rowcol for WMFire data.\n
    """

    # Check parent_dict exists
    if not isinstance(parent_dict, dict) or not isinstance(data, pd.DataFrame) or not isinstance(variable, str) or not isinstance(groupby, list):
        raise TypeError('Either parent_dict, data, or variable are not correct types.')  # TODO: Could make this a function itself and check each individually and raise error

    if variable not in data.columns:
        raise ValueError('variable is not found in data.')
    
    # Check that all groupby elements exist in data
    if not bool(set(groupby) & set(data.columns)):
        raise ValueError('groupby elements not found in data.')
    
    data_copy = data
    
    # data_copy = data_copy[groupby+list(variable)].groupby(groupby, sort=False)  # sort=False keeps columns in original order
    data_copy = data_copy[groupby+[variable]].groupby(groupby, sort=True)  # sort=True to sort by either rowcol or patchID
    count = data_copy.count()  # produces series
    cumsum = data_copy.sum()   # produces series

    # Check if child dict already exists in parent
    if (variable in parent_dict and 
        isinstance(parent_dict[variable], dict) and
        'count' in parent_dict[variable] and 
        isinstance(parent_dict[variable]['count'], np.ndarray) and
        'cumsum' in parent_dict[variable] and 
        isinstance(parent_dict[variable]['cumsum'], np.ndarray)
        ): # add the two np arrays to existing
            # if parent_dict[variable]['count'].size == count[variable].values.size and parent_dict[variable]['cumsum'].size == cumsum[variable].values.size
            parent_dict[variable]['count'] += count[variable].values
            parent_dict[variable]['cumsum'] += cumsum[variable].values
    else:  # create new dictionary with the np.arrays and save it to parent_dict as variable 
        parent_dict[variable] = {
            'count': count[variable].values,
            'cumsum': cumsum[variable].values,
            # 'patchID': count.index  # testing - to compare with spat_coord['patchID'] to see if correct order
        }

    #global testvar  # testing cyclical dependency
    #testvar = cumsum  # testing cyclical dependency
    
    return parent_dict


def ftbl_stats(data: pd.DataFrame, nyrs: int, barea: int, eco=True) -> dict:
    """Analyzes basin scale fire table for descriptive statistics on fire\n
    size, frequency, and occurence density. Also, considers LitLoad and RelDef,
    if `eco` is set as True.
        data [pd.DataFrame]: table containing unique temporal indicators (syr and smth),\n
            fire size, and optionallly mean surface litter carbon (LitLoad) & evap. relative deficit (RelDef)\n.
        nyrs [int]: number of years elapsed during the simulation.\n
        barea [int]: number of grid cells in basin modeled, represents basin size.\n 
        eco [bool]: If true checks for LitLoad and RelDef and calculates mean, median, and 90th percentile amoung,
            fire events.
    """
    if not isinstance(data, pd.DataFrame) and not isinstance(eco, bool):
        raise ValueError("data or eco is invalid.")

    if data.empty:
        return None
    
    if 'SpreadIter' not in data.columns:
        raise ValueError("data does not contain fire size info (SpreadIter).")
    
    if 'smth' not in data.columns:
        raise ValueError("data does not contain simulation months info (smth).")
    
    bas = dict()

    # size
    bas['size'] = mm90(data, 'SpreadIter')

    # density
    bas['density'] = dict()
    bas['density']['aburn'] = float(round(data['SpreadIter'].sum(), ndigits=3))
    bas['density']['nfr'] = float(round(nyrs*barea/bas['density']['aburn'], ndigits=3))

    # frequency
    bas['frequency'] = dict()
    bas['frequency']['nfire'] = int(data['SpreadIter'].count())
    bas['frequency']['pfire'] = float(round(bas['frequency']['nfire']/nyrs, ndigits=4))
    
    # Get FRI (data should already be sorted in order, not the responsibility of this function)
    data['dt'] = data.smth.diff()/12
    bas['frequency']['fri'] = float(round(data['dt'].mean()))

    if eco == True:
        for ecovar in ['LitLoad', 'RelDef']:
            if ecovar not in data.columns:
                raise ValueError(f'data does not contain ecological variable {ecovar}.')
            bas[ecovar] = mm90(data, ecovar)  # mean, median, 90thpctile


    return bas
        

def mm90(data: pd.DataFrame, var: str) -> dict:
    """Calcuates mean, median, and 90th percentile for data and saves to dict."""

    mm90 = {
        'mean': float(round(data[var].mean(), ndigits=3)),
        'median': float(round(data[var].median(), ndigits=3)),
        '90pctile': float(round(data[var].quantile(0.9), ndigits=3))
    }

    return mm90


def convert_ndarray_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def convert_nested_ndarray(obj: dict):
    for item in obj:
        if isinstance(obj[item], dict):
            convert_nested_ndarray(obj[item])
        elif isinstance(obj[item], np.ndarray):
            obj[item] = obj[item].tolist()
    
    return obj

def tidy_json(data: dict, start_str: str="{\n", end_str="}", indent: int=0):
    string = start_str
    indent = indent
    for index, item in enumerate(data):        
        # keystr = '\n' + '\t'*(indent+1) + "\"" + item + "\"" + ': '
        keystr = '\t'*(indent+1) + "\"" + item + "\"" + ': '
        if isinstance(data[item], dict):
            string += keystr + ' {\n'  # TODO: Maybe first element shouldn't have newline
            string = tidy_json(data[item], start_str=string, end_str="", indent=indent+1)            
            string += '\t'*(indent+1) + '}'
        else:
            string += keystr + json.dumps(data[item], indent=None)

        if index+1 != len(data):
            string += ','
        string += '\n'
    string += end_str
    return string


def getlen(obj):
    if isinstance(obj, str):
        return 1
    else:
        try:
            return len(obj)
        except Exception:
            return 1
    

def print_dict(pydict: dict, indent=0):
    """Prints python dictionary pretty."""
    for key, value in pydict.items():
        if isinstance(value, dict):
            print('   '*indent + f"{key}:")
            print_dict(value, indent=indent+1)
        else:
            print('   '*indent + f"{key}: {value}")


def dict_struct(pydict: dict, lvl: int=0):
    """Returns a dictionary detailing the structure of `pydict`.\n
    The structure defines the class, length, and level of each key-value.\n
    For key-values that are pd.Dataframes, also contains shape.
    """
    struct = dict()
    for key in pydict:
        item = pydict[key]
        subdict = {
            'lvl': lvl,
            'class': item.__class__.__name__,
            'n': getlen(item)
        }

        if isinstance(item, dict):
            for subkey, subvalue in dict_struct(item, lvl+1).items():
                subdict[subkey] = subvalue
        elif isinstance(item, pd.DataFrame):
            subdict['shape'] = item.shape

        struct[key] = subdict

    return struct


def value_from_keypath(pydict: dict, keypath: list, replacement=None, replace: bool = False):
    """Accesses a ditionary key-value based on a keypath.
        keypath [list|tuple]: contains dictionary keys to index `pydict`, read\n
            from left to right. ('a1', 'a11', 'a111') is synonymous with pydict['a1']['a11']['a111']
    """
    current_dict = pydict
    last_key = keypath[-1]

    try:
        if len(keypath) > 1:
            for key in keypath[:-1]:
                current_dict = current_dict[key]
            dict_value = current_dict[last_key]
        else:
            dict_value = current_dict[last_key]
    except (KeyError, TypeError):
        return None

    if replace:
        current_dict[last_key] = replacement
        return pydict
    else:
        return dict_value


def dict_stats(pydicts: list, keypath: list, stat: str='sum'):
    """Calculates prescriped `stat` for all dictionary key-value pairs in\n
    `pydicts` specified by `keys`. By default, all keys other than `keys`,\n
    found in the first dict in `pydicts` are presered (no stats done).\n

        pydict [list]: list of dictionaries to perform statistics on.\n
        keys [list]: list of keypaths to perform that statistics on in each dict.\n
            key paths are tuples specifying nested dict layers from Left-> right.\n
            For example the keypath for ex_dict['key1']['key2']['key3'] = ('key1','key2','key3').\n
        stat [str]: stat to perform, either `sum`, `mean`, or `count`.\n

    *All dictionaries must have the same structure (via dict_struct) for this to work*.
    """
    structs = list()
    keyvalues = list()
    for pydict in pydicts:
        structs.append(dict_struct(pydict))
        keyvalue = value_from_keypath(pydict, keypath)
        if not isinstance(keyvalue, np.ndarray) and not keyvalue is None :
            keyvalue = np.array(keyvalue)
        keyvalues.append(keyvalue)

    if not all(item == structs[0] for item in structs[1:]):
        raise ValueError('One or more dictionaries in pydicts have a different structure.')
    
    if any(item is None for item in keyvalues):
        raise ValueError('One ore more keyvalues are `None` and stats can not be performed')
    
    # assuming all keyvalues have same class (they should after comparing structs)
    # then stack them into a single array
    keyvalues = np.stack(keyvalues)

    # perform the stat
    if stat == 'count':
        value = np.tile(keyvalues.shape[0], keyvalues.shape[1])
    elif stat == 'mean':
        value = np.mean(keyvalues, axis=0)
    elif stat == 'sum':
        value = np.sum(keyvalues, axis=0)
    else:
        value == None

    return value


if __name__ == '__main__':

    # dat = pd.DataFrame({
    #     'syr': [1, 100, 200, 300, 400, 500],
    #     'smth': [1, 1200, 2400, 3600, 4800, 6000],
    #     'SpreadIter': [5000, 20000, 17000, 27000, 15000, 25000],
    #     'LitLoad': [0.8, 1.0, 0.95, 1.2, 0.9, 1.1],
    #     'RelDef': [0.5, 0.8, 0.7, 0.9, 0.75, 0.85]}
    # )

    # ftbl_stats(dat, 1000, 27300)
    
    datdict1 = {
        'a': {
            'a1': ['one', 'two', 'three'],
            'a2': {
                'a21': 'four',
                'a22': 'five',
                'a23': 'six'
            }
        }, 'b': {
            'b1': [1, 2, 3],
            'b2': {
                'b21': 9,
                'b22': 10
            }
        }
    }

    datdict2 = {
        'a': {
            'a1': ['1', '2', '3'],
            'a2': {
                'a21': 'six',
                'a22': 'seventy',
                'a23': 'quatro'
            }
        }, 'b': {
            'b1': [5, 6 ,7],
            'b2': {
                'b21': 2,
                # 'b22': np.array([30, 20])
                'b22': 30
            }
        }
    }

    datdict3 = datdict1.copy()

    # datdict3 = value_from_keypath(datdict3, ('b','b1'), replacement=dict_stats([datdict1, datdict2], ('b','b1'), 'sum'), replace=True)
    val = dict_stats([datdict1, datdict2], ('b','b1'), 'sum')
    datdict3 = value_from_keypath(datdict3, ('b', 'b1'), replacement=val, replace=True)  # replace in place  # TODO: Beware, this saves replacement as np.ndarray ,...
    # TODO: so if a subsequent dict_stats is called it may cause problems when comparing structure because orginal was list not np.ndarray.
    # print(datdict3)
    print_dict(datdict3)
    
    # tjson = tidy_json(datdict)
    # print(tjson)

    #ds1 = dict_struct(datdict1)
    #print_dict(ds1)

    # ds2 = dict_struct(datdict2)

    #print(ds1 == ds2)  # two struct dictionaries are the same means same strucutre!

