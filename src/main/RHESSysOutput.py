# ------------------------------------------------------------------
# 2023-04-26
# Class objects that represent RHESSys output#
# 
# Progress:
# csv.sniff() doesn't handle fields with variable white space (which happens when you manulaly use a tab key to create tables)
# csv.DictReader also doesn't take regex expressions for variable whitespace so you can't manually put it there
# Solution: use ' ' as delimiter for csv.DictReader() and then when csv.DictReader.fieldnames is called, manually remove elements that are blank or whitespace ->
# This means [field for field in csv.DictReader.fieldnames if field not in ['', ' ', '\t']]
# Also manually change self.source_delim to '\s+' so that when pd.read_csv() is called, it can handle the variable whitespace or tab charcter.
# Otherwise it will handle commas, |, or ;, etc.
# ------------------------------------------------------------------

import os
import pandas as pd
import numpy as np
import csv
from typing import Iterable
import re

#class RHESSysOutput(Tabular):  # TODO: use generators when applicable & make it able to read different input file formats and handle large datasets!
class Tabular(object):  # TODO: Create RHESSysOutput Subclass
    """
    `Purpose:` Extract data from RHESSys output file, then manipulates it to the user’s needs. Contains several attributes to specify source location,\n 
        spatial, temporal, and identification fields, as well as what format the imbedded data table is in.

    `Attributes:`
        source [list]: path to source file of RHESSys output.\n
        source_delim [str]: delimitor character that separates fields in text file.\n
        source_exists [bool]: if True, source file exists.
        
        num_fields [int]: number of fields in data.\n
        fields [list]: ordered lists all fields in the data as it appears (left->right). Updates with .getfields().\n
        time_fields [list | set]: list of all fields that describe temporal time scale.\n
        spat_fields [list | set]: list of all fields taht describe spatial time scale.\n
        id_fields [list | set]: list of all fields that uniquely idenfity the data.\n
        var_fields [list | set]: list of all fields that are variables from model output.\n
        
        req_time_fields [None | iter]: iterable of requested time field names to extract from source. None returns all.\n
        req_spat_fields [None | iter]: iterable of requested spat field names to extract from source. None returns all.\n
        req_id_fields [None | iter]: iterable of requested id field names to extract from source. None returns all.\n
        req_var_fields [None | iter]: iterable of requested var field names to extract from source. None returns all.\n
        
        abs_time_fields [None | iter]: iterable of absent time field names found by xref(self.req_time_fields, self._fields).\n
        abs_spat_fields [None | iter]: iterable of absent spat field names found by xref(self.req_spat_fields, self._fields).\n
        abs_id_fields [None | iter]: iterable of absent id field names found by xref(self.req_id_fields, self._fields).\n
        abs_var_fields [None | iter]: iterable of absent var field names found by xref(self.req_var_fields, self._fields).\n
        
        valid_time_fields [list | set]: list of valid field names used to classify temporal scale.\n
        valid_spat_fields [list | set]: list of valid field names used to classify spatial scale.\n

        stat_format [bool]: specifies whether statistics have been performed on data.\n
            If false, data is still raw.\n

        data [pd.DataFrame]: RHESSys output data in tabular format.\n

    `methods:`
        __init__: initialized the object; Defines initial value of attributes by calling `.getfields()`, `.getscale()` and `.populate()`.\n
        getfields: extracts field names for the data from either the source file (.source) or data (.data).\n
        getscales: classifies the spatial (.spat_scale) and temporal (.time_scale) scales based on `.spat_fields` and `.time_fields`.\n
        populate: extracts RHESSys output data from `.source`.\n
        aggregate: aggregates `.data` to a specified temporal or spatial scale.\n
        mutate: reformats `.data` to meet the user's needs. (Tasks can vary).\n
        remove: removes a list of fields from .data.\n
        join: joins the `RHESSysOutput` object with another.
        stats: performs statistical analysis on `.data`.\n
    """
    # TODO: RHESSysOutput Sublcass fieldclass_rules
    _fieldclass_rules = {
        'temporal': ['cent', 'dec', 'year', 'month', 'week', 'day'] + ['scent', 'sdec', 'syr', 'smth', 'swk', 'sday'],
        'spatial': ['basinid', 'hillid', 'hillslopeid', 'zoneid', 'patchid', 'stratumid', 'vegid']
    }

    # def __init__(self, source=None, time_scale=None, spat_scale=None):  # TODO: determine how to handle desired time and spatial scales and other target variables
    def __init__(self, source: str|None=None, fields: list|None=None, populate: bool=True):
        """Initialization of RHESSysOutput object.""" 
        
        self.source=[source]
        self.source_delim = None
        self.source_exists = False
        
        # current data fields of .data
        # self._fieldclass_rules = dict()  # valid values for each class  # Defined as Class Attribute instead
        self._fieldclass = dict()  # field names for different field classes
        self._fields = []  # all field names
        # self._fields_req = []  # requested to extract
        self._fields_abs = []  # absent from request
        self._num_fields = None
        
        self.data = None

        # check source exists
        self.test_source()

        # Populate
        if populate == True:
            try:
                # self.populate()  # populate the data
                self.populate(fields=fields)  # cross reference request fields with available fields
            except:  # anything will work
                print("Failure to populate from source.")

    def test_source(self):
        """Tests if the source file exists."""
        self.source_exists = os.path.exists(self.source[0])

    def addfieldclass(self, name: str, fields: list) -> None:
        """Adds a fieldname classification to .fieldclass_rules so when .getfields() is called it is classifed.\n
        name [str]: name of field classification. All unclassified fields become variables.\n
        fields [list]: list of field names that fall into the class.\n
        return: None
        """
        try:
            if name.__class__.__name__ != 'str' or fields.__class__.__name__ != 'list':
                raise ValueError('In addfieldclass(): Either `name` is not a string, `fields` is not a list, or both.')
            self._fieldclass_rules[name] = fields
        except Exception as e:
            print(f'Exception raised during addfieldclass(): {e}.')

        return None
    
    def getfields(self, source="data") -> None:
        """Function to get field names of RHESSys data.\n
            
            1st - check if file exists opens file in read mode.\n
            2nd - removes all blank leading lines.\n
            3rd - grab first line of text.\n
            4th - split text into fields deliminator.\n
            
            source [str]: specifies the source to get fields:\n
                `data` will extract from the data attribute of self.\n
                `source` will extract from the source file of self.\n
        """
        # First update self._fields
        # if source == "source" and os.path.exists(self.source[0]): # Get fields from source file
        if source == "source" and self.source_exists: # Get fields from source file
            dialect = dsniff(self.source[0])  # Create a dialect using the non-blank lines

            # Update the source_delim                
            if dialect.delimiter in [' ', '\t']:  # csv.DictReaders can't handle field delimiters with multiple characters or fields with variable whitespace
                self.source_delim = r'\s+'  # set it to the regex expression for whitespace of variable level for when pd.csv_read() is called to prevent crash
            else:
                self.source_delim = dialect.delimiter
                    
            # Extract the header row
            with open(self.source[0], 'r') as srcfile:
                # srcfile.seek(0)  # reset cursor
                srcfile.seek(dialect.hdr_byte_pos)  # set cursor to start of header row (dialect from dsniff())
                
                # Create csv.DictReader object
                reader = csv.DictReader(srcfile, delimiter=dialect.delimiter, dialect=dialect)  # generator to return each line of csv
                
                # Save fields to class attributes, ordered as they appear (L->R) and removing blankspace column names
                self._fields = [field.strip() for field in reader.fieldnames if field not in ['', ' ', '\t']]  # remove white space elements from fieldnames if applicable

        elif source == "data": # get field names from self.data()
            self._fields = self.data.columns.tolist()  # ordered list of fields as they appear (L->R)
        
        # Update fieldclasses
        self._num_fields = len(self._fields)
        for cl in self._fieldclass_rules:  # custom classes
            self._fieldclass[cl] = [field for field in self._fields if field.casefold() in self._fieldclass_rules[cl]]

        # self.id_fields = {field for field in [field for field in self._fields if field.endswith('ID')]} - self.time_fields - self.spat_fields # TODO: if you don't know which fields are ids
        # self._fieldclass['variable'] = list(set(self._fields) - {field for fieldlist in self._fieldclass_rules.values() for field in fieldlist})  # TODO: there should be no rule for 'variable'
        self._fieldclass['variable'] = [field for field in self._fields if field.casefold() not in [field.casefold() for fieldlist in self._fieldclass_rules.values() for field in fieldlist]]
        
        for cl in self._fieldclass:
            print(f'{cl}: {self._fieldclass[cl]}')

        return None

    def populate(self, fields: list|None):  # TODO: determine how to apply filters/ how to load in chunks (for files too large to read into format) with *args and **kwargs
        
        # Initialize fields from source (and delim)        
        if self.source_exists:
            self.getfields("source")

            # Cross reference field requests (can use self._fields) (position matters)
            try:
                if fields != None:
                    fields_avail, fields_abs = xref(fields, self._fields)
                else:
                    # fields_avail, fields_abs = xref(None, self._fields)
                    fields_avail, fields_abs = self._fields, []
            except Exception as e:
                print("Exception occured in self.populate() during cross referencing field requests: {e}.")
                return None

            # Query for index position from self._fields # TODO: Unnecessary with headers

            # Extract fields data from source into pandas dataframe
            try:
                self.data = pd.read_csv(self.source[0], delimiter=self.source_delim, 
                usecols=list(fields_avail))
                self._fields_abs = list(fields_abs)
            except Exception as e:
                print("Exception occured in self.populate() during data extraction: {e}.")
                return None
            
            self.getfields()

        return None

    def mutate(self, column: str, formula: str) -> None:
        """Applies `formula` to `column` in `.data` using .eval(). Basically acts as an anonymous function (like lamba).\n
        
        column [str]: name of the column to mutate.\n
            ex: 'index'.\n
        
        formula [str]: string with the formula to apply to the column.\n
            ex: '(col1 + col2)/2'\n
        
        example - if column = "index" and formula = "(col1 + col2)/2" the following code will be executed on self.data:\n
            \n
                self.data = self.data.eval('column = (col1 + col2)/2)')\n
        """
        # create a copy of the data DataFrame to avoid modifying the original
        data_copy = self.data.copy()
        
        try:
            # use assign method to create a new column with the modified values
            # data_copy[column] = data.eval(formula)
            data_copy = data_copy.eval(column + " = " + formula)  # formula is practically a lambda or anonymous function
            
            # update the .data attribute with the modified DataFrame
            self.data = data_copy
            
            # Update fields
            self.getfields()

        except Exception as e:
            print(f"Exception raised in self.mutate(): {e}.")
            
        return None

    def remove(self, fields: list = None) -> None:
        if fields:
            data_copy = self.data.copy()
            try:
                data_copy.drop(fields, axis=1, inplace=True)
                self.data = data_copy
                self.getfields()
            except KeyError as e:
                print(f"KeyError raised in self.remove(): {e}.")

        return None

    def concat(self, objs: Iterable['RHESSysOutput'], axis=0, copy=True, **kwargs) -> None:
        """
        Concatinates two RHESSysOutput object's data and update instance attributes. Uses pandas.DataFrame.concat() as method of combining.\n
        The two dataframes must have a common dimension to concatinate. By default concat is in the 0 dimension (row-wise).
        """
        try:
            data_copy = pd.concat([self.data] + [obj.data for obj in objs], axis=axis, copy=copy, **kwargs)
            self.data = data_copy  #TODO: Reset row_id
            self.getfields()
            source_copy = self.source + [obj.source[0] for obj in objs]
            self.source = source_copy
        except Exception as e:
            print(f"Exception raised during self.concat(): {e}.")

        return None

    def merge(self, right: 'RHESSysOutput', left=None, how='outer', **kwargs):
        """
        Merges two RHESSysOutput Object's data and updates attributes accordingly. Uses pandas.DataFrame.merge() as method of combining.\n
        The user specifies which field(s) to merge the two columns on, and they can be either the same name or not. It is advised that the\n
        the merge fields are in the same format.\n

        on: list or array object specifying columns to merge on.\n
        left_on: list or string specifying field(s) to join on left.\n
        right_on: list or string specifying the field(s) to join on right.\n
        how: how to merge the two dataframes: inner=only matching rows, outer=all rows and fill with Nan, left=all rows from left df and matching rows of right, right=opposite of left.\n
            ex) left_on = ['A', 'B'] and right_on = ['A', 'C'] will join rows where left df's 'A' and 'B' columns equal right df's 'A' and 'C' columns respectively.\n
        """
        try:
            data_copy = pd.merge(left=self.data, right=right.data, how=how, **kwargs)
            self.data = data_copy
            self.getfields()
        except Exception as e:
            print(f"Exception raised during self.merge(): {e}.")
        
        return None

    def aggregate(self, *args):  # TODO: write
        """Aggregates data. Selects spatial or temporal variables to group by, and then performs operation accordingly.
        Should also be able to handle state variables vs fluxes."""
        pass

    def stats(self, *args):  # TODO: write
        """Performs statistics on data.
        Returns a dataframe rather than editing data directly"""

    def getstats(self, *args):  # TODO: write
        """Performs stats on data using stats() method."""
        

    def getscales(self):  # not sure if this is necessary yet
        """Based on available spatial, time, and id fields, updates the time_scale and spat_scale attributes.
        time scales:\n
            daily = time_fields contains [day, month, year]
            monthly = time_fields contains [month, year] but not [daily].\n
            yearly = time_fields contains [year], but not [month, daily].\n
            custom = every other combination

        spat scales:\n
            stratum = spat_fields contains [vegID, stratumID, patchID, zoneID, hillslopeID, and basinID] 
            patch = spat_fields contains [patchID, zoneID, hillslopeID, basinID], but not [vegID, stratumID]
            zone = spat_fields contains [zoneID, hillslopeID, basinID], but not [vegID, stratumID, patchID]
            hillslope = spat_fields contains [hillslopeID, basinID], but not [vegID, stratumID, patchID, zoneID]
            basin = spat_fields contains [basinID], but not [vegID, stratumID, patchID, zoneID, hillslopeID]
            custom = every other combination
        """
        
        return None
    

def xref(x, y):
    """Cross references list x in y, and returns all values found within. Search is case-insensitive.\n
        x [iter]: values to be searched for.\n
        y [iter]: values available (warehouse).\n
        avail [list]: list of values found in y.\n
        unavail [list]: list of values not found in y.\n
        return [tuple]: returns a tuple of avail and unavail.
    """
    avail = []
    unavail = []
    if x:
        for item in x:
            if item in y:
                avail.append(item)
            else:
                unavail.append(item)
    else:
        avail = y
        unavail = []
    return avail, unavail


def dsniff(file: str) -> csv.Dialect:
    """
    Sniffs a text file in tabular format for a csv.dialect using csv.sniff(). Skips leading whitespace/blank lines, but blank files\n
    return a value of None. The dialect contains informatuion such as delimiter detected and can be used to create a csv.reader object\n
    and identify the header (if it exists) of a tabular text file.

    file [str]: str containing the path to textfile to parse for the tabular delimiter.\n
    return [tuple]: tuple containing a) single length character string containing the delimiter of the text file,\n
        and b) a list of header
    """

    with open(file, 'r') as srcfile:                
        # Skip all blank lines at begining of file
        while True:
            line = srcfile.readline()
            # print(line)

            if line == '':
                break  # EOF
            elif line.strip() != '':
                break  # Blank line

        if line == '':  # handles blank source files
            raise ValueError("File is blank")
        
        hdr_byte_pos = srcfile.tell() - len(line)
        srcfile.seek(hdr_byte_pos)
        
        # Create a dialect using the non-blank lines
        dialect = csv.Sniffer().sniff(srcfile.readline())  # dialect = csv.Sniffer().sniff(srcfile.read(5000))  # fails
        dialect.hdr_byte_pos = hdr_byte_pos

        return dialect


class Statobj(object):
    """Methods only allow for one grouping method of the data. For example, if the target groups are basinID, year, then data will be grouped by this only."""
    def __init__(self, data: pd.DataFrame, group_fields: list) -> None:
        self.data = data  # pd.dataframe() original dataset -> linked to RHESSysOutput.data or pass data.copy or data.deepcopy() to avoid.
        self.group_fields = group_fields
        self.group_fields_data = self.data.drop_duplicates(subset=self.group_fields)[self.group_fields]  # All unique rows of the groups
        self.stats = {}

    def addstat(self, stat: str, fields: list, pctile: int = 90, int_stat: str|None = None, int_group_fields: list|None = None, int_pctile=90, drop_group_fields=True) -> None:
        """Calculates a statistics for self.data grouped by self.group_fields, then stores the\n
            resulting dataframe to self.stats. If int_stat and int_group_fields are provided,\n
            performs a preliminary statistical calculation on the data based on these arguements.\n
            
            Needs to check if a stat already exists, and make sure to keep all group_fields from\n
            self.group_fields during first preliminary statistical operation if performed.

            return None
        """
        data_copy = self.data.copy()
        statname = stat

        if stat == "pctile":
             statname= str(pctile) + statname

        # Preliminary statistical operation (if applicable)
        if bool(int_stat) and bool(int_group_fields):
            int_group_fields = list(set(self.group_fields) | set(int_group_fields))
            data_copy = data_copy[int_group_fields + fields]
            data_copy = getstat(data_copy, groups=int_group_fields, stat=int_stat, pctile=int_pctile)
            statname = int_stat + "&" + statname

        # Primary statistical operation
        data_copy = data_copy[self.group_fields + fields]
        data_copy = getstat(data_copy, groups=self.group_fields, stat=stat, pctile=pctile)

        if drop_group_fields == True:
            data_copy = data_copy.drop(self.group_fields, axis=1)

        self.stats[statname] = data_copy

        return None

    
    def stat_list(self, stat):
        """Returns list of fields calculated for a specific stat."""
        pass

    def stat_dim(self, stat):
        """Returns the dimensions of a certian stat dataframe."""
        pass

    def select_data(self, id_merge: bool=True, long_format: bool=False) -> pd.DataFrame:
        """Returns stat data for a single statistic. id_merge=True will merge with the .id data."""
        pass

    def combine_data(self, stats: list, id_merge: bool=True, long_format: bool=False) -> pd.DataFrame:
        """Returns stat data for multiple statistics. id_merge=True will mere with .id data. """
        # TODO: Check that fields are not repreated when merged. If they are repeated then do "stat" + "field" -> <stat>_<field>.
        # TODO: Also give option to format data in long-format where rows are linked to a certain stat identifier.
        pass

    def populate(self, data, id_fields, settings):
            """Calculates statistics based on data, id_fields, and stats parameters."""
            pass

    def update_data(self):
        """This will merge"""

# Need to add a method to getfields() so that it is for a stat object.
# TODO: Figure out how to do stepwise stats, such as daily precip -> monthly precip -> average monthly precip/yr

def getstat(data: pd.DataFrame, groups: list, stat: str="mean", pctile: int=90) -> pd.DataFrame:
    """
    Performs a statistical operation on input dataframe `data`.\n
        groupby [list]: list of fields to group data by before performing statistical operation.\n
        stat [str]: statistic to calculate, valid options: `count`, `sum`, `mean`, `pctile`, `var`, `std`.\n
        pctile [int]: pctile to calculate if `stat=pctile`.\n
        return [pd.Dataframe]: dataframe after statistical operation is performed.
    """
    
    data_copy = None
    if bool(groups):
        try:        
            # data_copy = data.groupby(groups).copy()
            data_copy = data.groupby(groups)
            if stat == 'count':
                data_copy = data_copy.count()
            elif stat == 'sum':
                data_copy = data_copy.sum()
            elif stat == 'mean':
                data_copy = data_copy.mean()
            elif stat == 'pctile':
                data_copy = data_copy.quantile(pctile/100)
            elif stat == 'var':
                data_copy = data_copy.var()
            elif stat == 'std':
                data_copy = data_copy.std()
            else:
                pass
        except ValueError as e:
            print(f"ValueError: {e}.")
        except AttributeError as e:
            print(f"AttributeError: {e}.")
        else:
            data_copy = data_copy.reset_index(drop=False)

    else:
        raise ValueError("`groups` is not a list of valid fields.")
    
    return data_copy

def read_csv(file, *args):
    """Reads a csv file completely into memory."""
    return None


def read_csv_chunks(file, *args):
    """Reads a csv file chunkwise."""
    return None


if __name__ == "__main__":

    # Testing
    req_var = ['gpsn', 'psn', 'plantc']
    # rhessys1 = RHESSysOutput("./test.daily")
    # rhessys1 = RHESSysOutput("./test-hist-fire-1_basin.daily", var_fields=req_var)
    # rhessys1.mutate('sn', '(psn + gpsn)/2')
    # rhessys1.remove(['smth', 'sday', 'syr'])
    # rhessys1.mutate('sn2', '(psn + gpsn)/4')
    # r1 = RHESSysOutput("./test1.daily")
    # r2 = RHESSysOutput("./test2.daily")
    # r3 = RHESSysOutput("./test3.daily")
    # print()
    # print(r1.data)
    # print()
    # print(r2.data)
    # print()
    # print(r3.data)
    # print()
    # r1.concat([r2])
    # del r2
    # print(r1.data)
    # print()
    # merge_fields = list(r1.time_fields.copy()) + list(r1.spat_fields.copy())
    # r1.merge(right=r3, on=merge_fields)  # TODO: Debug
    # del r3
    # print(r1.data)
    # print()
    r1 = Tabular("./test1.daily")
    # print()
    # print(r1.data)
    # print()
    r1.stats = Statobj(r1.data, group_fields = ['basinID', 'year'])
    print()
    print(f"data:\n{r1.stats.data}\n")
    print(f"group_fields_data:\n{r1.stats.group_fields_data}\n")
    
    
    # r1.stats.addstat('sum', ['var2'], drop_group_fields=False)
    # r1.stats.addstat('mean', ['var2'], drop_group_fields=False)
    r1.stats.addstat('mean', ['var2'], int_stat='sum', int_group_fields=['month'], drop_group_fields=False)
    for stat in r1.stats.stats:
        print(f"{stat}:\n{r1.stats.stats[stat]}\n")
