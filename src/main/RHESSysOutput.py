# ------------------------------------------------------------------
# 2023-04-26
# Class objects that represent RHESSys output#
# ------------------------------------------------------------------

import os
import pandas as pd
import numpy as np

class RHESSysOutput(object):  # TODO: use generators when applicable & make it able to read different input file formats and handle large datasets!

    def __init__(self, source=None, time_scale=None, spat_scale=None):  # TODO: determine how to handle desired time and spatial scales and other target variables
        """Initialization of RHESSysOutput object.""" 
        self.source=source
        self.time_scale=time_scale  # tuple of desired time_scale fields (used for aggregation)
        self.spat_scale=spat_scale  # tuple of desired spat_scale fields (used for aggregation)
        self.data = None
        self.fields = []
        self.id_fields = []
        self.time_fields = []
        self.spat_fields = []
        
        # Populate if all data is provided
        if source and time_scale and spat_scale:
            try:
                self.get_fields()  # function to extract fields from source and save to self.fields, self.id_fields, self.time_fields, self.spat_fields
                self.data = self.populate(source=self.source, )
            except:  # TODO: find exceptions
                pass

    def populate(self, source, time_scale, spat_scale):  # TODO: write, determine how to apply filters, handle different input formats, and handle files too large to readinto memory
        pass

    def reformat(self, *args):  # TODO: write
        pass

    def aggregate(self, *args):  # TODO: write
        pass

    def stats(self, *args):  # TODO: write
        pass

    # TODO: Whenever the columns change from a method, call .get_fields() method to update the fields


    
