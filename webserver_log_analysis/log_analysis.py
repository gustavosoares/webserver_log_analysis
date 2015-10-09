import logging
import os
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from prettytable import PrettyTable
from colors import Colors
import numpy as np
import datetime as dt

from influxdb import DataFrameClient

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
LOG = logging.getLogger(__name__)


class LogAnalysis(object):

    def __init__(self, options={}):

        self.access_log = options.get("access_log")
        self.log_datetime_format = options.get("log_datetime_format", '%d/%b/%Y:%H:%M:%S')
        self.plot_chart = options.get("plot_chart", False)
        self.request_time_threshold = options.get("request_time_threshold", 10)
        self.uri_white_list = options.get("uri_white_list", [])
        self.columns = ['time_local','request_method','request_uri','status','request_time',]
        self.table_columns = ['request_uri','mean','min','max','std']
        self.table = PrettyTable(self.table_columns)
        #statsd
        self.stats_client = options.get("stats_client", None)
        self.influxdb_client = options.get("influxdb_client", None)

    def __send_to_influxdb(self, data_frame=None):
        """
        key should be a string delimited by point
        eg: a.b.c

        to send data to statsd: self.stats_client.incr(key, value)
        """
        LOG.debug("sending dataframe to influxdb")
        if self.influxdb_client and data_frame is not None:
            df = data_frame
            white_list = self.uri_white_list
            LOG.info("uri white list => {0}".format(white_list))
            for uri in white_list:
                df_aux = df[df.request_uri == uri]
                df_aux = df_aux.drop(df_aux.columns[[1, 2, 3]], axis=1)
                df_aux = df_aux.set_index(['time_local'])
                uri_list = uri.split('/')
                table_name = '_'.join([x for x in uri_list if x])
                LOG.debug("sending data to table {0}".format(table_name))
                self.influxdb_client.write_points(df_aux, table_name)

    def __round(self, number):
        return "%.2f" % number

    def __plot_chart(self, data_frame=None):

        df = data_frame
        white_list = self.uri_white_list
        LOG.info("uri white list => {0}".format(white_list))
        #df_white_list = df[df['request_uri'].isin(white_list)]

        color = itertools.cycle(('b', 'g', 'r', 'c', 'm', 'y', 'k'))
        marker = itertools.cycle(('+', '*', 'x', 's', 'D'))

        # http://auctionrepair.com/pixels.html
        fig = plt.figure(figsize=(35,6.85))
        plt.title("Resquest time X Request URI - {0}".format(self.access_log))
        ax = fig.add_subplot(1,1,1)
        LOG.info("saving plot...")
        for uri in white_list:
            df_aux = df[df.request_uri == uri]
            ax.plot_date(df_aux['time_local'],
                    df_aux['request_time'],
                    fmt='b-',
                    marker=marker.next(),
                    color=color.next())

        ax.grid(color='k', linestyle='--', linewidth=0.2)
        locator = mdates.MinuteLocator(np.arange(0,60,30))
        locator.MAXTICKS = 2000
        ax.xaxis.set_minor_locator(locator)
        ax.xaxis.set_major_locator(mdates.HourLocator(np.arange(0,25,2)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%b/%Y:%H:%M'))
        ax.fmt_xdata = mdates.DateFormatter(self.log_datetime_format)
        ax.legend(white_list, loc='best', fancybox=True, framealpha=0.5)
        ax.set_xlabel('datetime')
        ax.set_ylabel('request time')
        fig.autofmt_xdate()
        fig.savefig("/tmp/webserver_log_analysis.png", format='png', dpi=600)
        LOG.info("done")

    def parse_dates(self, x):
        return dt.datetime.strptime(x, self.log_datetime_format)

    def run(self):

        if os.path.exists(self.access_log):
            columns = self.columns
            #df = pd.read_table(self.access_log, parse_dates=[0], date_parser=self.parse_dates, names=columns, sep='\s+', dtype={"status": np.int8, "request_time": np.float16})
            df = pd.read_table(self.access_log, parse_dates=[0], date_parser=self.parse_dates, names=columns, sep='\s+')
            #df = pd.read_table(self.access_log, names=columns, sep='\s+',)
            grouped_by_minute = df.groupby(df['time_local'].map(lambda x: (x.year, x.month, x.day, x.hour, x.minute)))
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

            if self.plot_chart:
                self.__plot_chart(data_frame=df)

            if self.stats_client:
                self.__send_to_statsd(data_frame=df)

            if self.influxdb_client:
                self.__send_to_influxdb(data_frame=df)
        else:
            print LOG.debug("file [{0}] does not exist".format(self.access_log))

        print self.table.get_string()
