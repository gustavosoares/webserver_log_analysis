import logging
import argparse
import os
from pandas import Series, DataFrame
import pandas as pd
from prettytable import PrettyTable
import numpy as np
import sys
import time
import traceback
from ConfigParser import SafeConfigParser


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class NginxProfiler(object):

    def __init__(self, options={}):

        self.access_log = options.get("access_log")
        self.table_columns = ['request_uri','mean','min','max','std']
        self.table = PrettyTable(self.table_columns)

    def __round(self, number):
        return "%.2f" % number

    def run(self):

        if os.path.exists(self.access_log):
            columns = ['time_local','request_method','request_uri','status','request_time',]
            df = pd.read_table(self.access_log, names=columns, sep='\s+')
            df_200 = df[df['status'] == 200]
            grouped = df_200.groupby('request_uri')
            # interested_in = ['/network/create/',
            #                  '/vip/remove/',
            #                  '/api/pool/save/']
            for name, group in grouped:
                desc = group.describe()
                mean = desc['request_time']['mean']
                min = desc['request_time']['min']
                max = desc['request_time']['max']
                std = desc['request_time']['std']
                self.table.add_row([name,
                                    self.__round(mean),
                                    self.__round(min),
                                    self.__round(max),
                                    self.__round(std)])
            # for name in interested_in:
            #     try:
            #         group = grouped.get_group(name)
            #         print name
            #         print group.describe()
            #         print "*" * 50
            #     except Exception, e:
            #         #LOG.warning("OPS... {0}".format(e))
            #         pass
        else:
            print LOG.debug("file [{0}] does not exist".format(self.access_log))

        print self.table.get_string()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Nginx profiler')
    parser.add_argument('--log', type=str, default='',
                        help='Logfile')

    args = parser.parse_args()

    parser = SafeConfigParser()

    access_log = args.log

    options = {"access_log": access_log,}
    nginx = NginxProfiler(options=options)
    nginx.run()