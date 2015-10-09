import logging
import argparse
import os
import sys
from ConfigParser import SafeConfigParser

from influxdb import DataFrameClient
import statsd

from log_analysis import LogAnalysis

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
LOG = logging.getLogger(__name__)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Nginx profiler')
    parser.add_argument('--log', type=str, default='',
                        help='Logfile')
    parser.add_argument('--request_time_threshold', type=int, default=10,
                        help='Threshold to color the row red')
    parser.add_argument('--plot_chart', type=bool, default=False,
                        help='Plot chart request time x request uri')
    parser.add_argument('--send_to_statsd', type=bool, default=False,
                        help='Send data to statsd. Need to specify the region too.')
    parser.add_argument('--send_to_influxdb', type=bool, default=False,
                        help='Send data to influxdb. Need to specify the region too.')
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
    send_to_statsd = args.send_to_statsd
    send_to_influxdb = args.send_to_influxdb
    uri_white_list = args.uri_white_list
    uri_white_list = uri_white_list.split(',')
    region = args.region

    stats_client = None
    influxdb_client = None
    if send_to_statsd and region:
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

    if send_to_influxdb and region:
        influxdb_host = "192.168.99.100"
        influxdb_port = 8086
        influxdb_user = 'root'
        influxdb_password = 'root'
        influxdb_dbname = 'log_analysis'

        influxdb_client = DataFrameClient(influxdb_host,
                                 influxdb_port,
                                 influxdb_user,
                                 influxdb_password,
                                 influxdb_dbname)

        influxdb_client.create_database(influxdb_dbname)

    options = {"access_log": access_log,
                "request_time_threshold": request_time_threshold,
               "log_datetime_format": log_datetime_format,
               "plot_chart": plot_chart,
               "uri_white_list": uri_white_list,
               "statsd": statsd,
               "stats_client": stats_client,
               "influxdb_client": influxdb_client}

    log_analysis = LogAnalysis(options=options)
    log_analysis.run()