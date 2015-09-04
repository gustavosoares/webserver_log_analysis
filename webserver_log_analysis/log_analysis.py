import logging
import argparse
import os
from pandas import Series, DataFrame
import pandas as pd
from prettytable import PrettyTable
from colors import Colors
import numpy as np
import sys
import time
import traceback
from ConfigParser import SafeConfigParser


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class LogAnalysis(object):

    def __init__(self, options={}):

        self.access_log = options.get("access_log")
        self.request_time_threshold = options.get("request_time_threshold", 10)
        self.table_columns = ['request_uri','mean','min','max','std']
        self.table = PrettyTable(self.table_columns)

    def __round(self, number):
        return "%.2f" % number

    def run(self):

        if os.path.exists(self.access_log):
            columns = ['time_local','request_method','request_uri','status','request_time',]
            #df = pd.read_table(self.access_log, names=columns, sep='\s+', dtype={"status": np.int8, "request_time": np.float16})
            df = pd.read_table(self.access_log, names=columns, sep='\s+',)
            df_200 = df[df['status'] < 300]
            grouped = df_200.groupby('request_uri')
            for name, group in grouped:
                desc = group.describe()
                mean = desc['request_time']['mean']
                min = desc['request_time']['min']
                max = desc['request_time']['max']
                std = desc['request_time']['std']
                c_init = Colors.OK
                if mean >= self.request_time_threshold:
                    c_init = Colors.FAIL
                self.table.add_row([c_init + name,
                                    self.__round(mean),
                                    self.__round(min),
                                    self.__round(max),
                                    "{0}{1}".format(self.__round(std), Colors.END)])
        else:
            print LOG.debug("file [{0}] does not exist".format(self.access_log))

        print self.table.get_string()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Nginx profiler')
    parser.add_argument('--log', type=str, default='',
                        help='Logfile')
    parser.add_argument('--request_time_threshold', type=int, default=10,
                        help='Threshold to color the row red')

    args = parser.parse_args()

    parser = SafeConfigParser()

    access_log = args.log
    request_time_threshold = args.request_time_threshold

    options = {"access_log": access_log,
                "request_time_threshold": request_time_threshold}

    log_analysis = LogAnalysis(options=options)
    log_analysis.run()