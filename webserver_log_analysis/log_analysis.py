import logging
import argparse
import os
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from prettytable import PrettyTable
from colors import Colors
import numpy as np
import datetime as dt
import sys
from ConfigParser import SafeConfigParser


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

    def __send_to_statsd(self, data_frame=None):
        """
        key should be a string delimited by point
        eg: a.b.c

        to send data to statsd: self.stats_client.incr(key, value)
        """
        if self.stats_client and data_frame:
            df = data_frame
            white_list = self.uri_white_list
            LOG.info("uri white list => {0}".format(white_list))
            for uri in white_list:
                df_aux = df[df.request_uri == uri]
                # ax.plot_date(df_aux['time_local'],
                #         df_aux['request_time'],
                #         fmt='b-',
                #         marker=marker.next(),
                #         color=color.next())

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
        else:
            print LOG.debug("file [{0}] does not exist".format(self.access_log))

        print self.table.get_string()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Nginx profiler')
    parser.add_argument('--log', type=str, default='',
                        help='Logfile')
    parser.add_argument('--request_time_threshold', type=int, default=10,
                        help='Threshold to color the row red')
    parser.add_argument('--plot_chart', type=bool, default=False,
                        help='Plot chart request time x request uri')
    parser.add_argument('--statsd', type=bool, default=False,
                        help='Send data to statsd. Need to specify the region too.')
    parser.add_argument('--log_datetime_format', type=str, default='%d/%b/%Y:%H:%M:%S',
                        help='date time log format. see python datetime for options.')
    parser.add_argument('--uri_white_list', type=str, default='',
                        help='uri white list coma delimited. Ex.: /a/,/b/,/test/')
    parser.add_argument('--region', type=str, default='', required=False,
                    help='statsd region')

    args = parser.parse_args()

    parser = SafeConfigParser()

    access_log = args.log
    request_time_threshold = args.request_time_threshold
    log_datetime_format = args.log_datetime_format
    plot_chart = args.plot_chart
    statsd = args.statsd
    uri_white_list = args.uri_white_list
    uri_white_list = uri_white_list.split(',')
    region = args.region

    stats_client = None
    if statsd and region:
        config_file = '~/.log_analysis'
        if not os.path.exists(config_file):
            LOG.warning("config file {0} not found")
            sys.exit(1)

        parser.read(os.path.expanduser(config_file))
        if parser.has_section(args.region):

         #Statsd
            if parser.has_option("Statsd", 'statshost'):
                statsHost = parser.get("Statsd", 'statshost')
            else:
                statsHost=None
                sys.exit("There is no statshost definition in Statsd section" )

            if parser.has_option("Statsd", 'statsPort'):
                statsPort = parser.get("Statsd", 'statsPort')
            else:
                statsPort=None
                sys.exit("There is no statsPort defined in Statsd section" )

            if parser.has_option("Statsd", 'statsProject'):
                statsProject = parser.get("Statsd", 'statsProject')
            else:
                statsProject=None
                sys.exit("There is no statsProject definition in Statsd section" )
        else:
            sys.exit("Invalid region: '%s'" % args.region)

    stats_client = statsd.StatsClient(statsHost, statsPort, prefix=statsProject)

    options = {"access_log": access_log,
                "request_time_threshold": request_time_threshold,
               "log_datetime_format": log_datetime_format,
               "plot_chart": plot_chart,
               "uri_white_list": uri_white_list,
               "statsd": statsd,
               "stats_client": stats_client,
               "stats_project": statsProject}

    log_analysis = LogAnalysis(options=options)
    log_analysis.run()