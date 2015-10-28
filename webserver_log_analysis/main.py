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


def read_value(parser, section=None, key=None):
    value = None
    if parser.has_option(section, key):
        value = parser.get(section, key)
        return value
    else:
        sys.exit("There is no {0} definition in section {1}".format(key, section))


def read_influxdb_conf():
    config_file = os.path.expanduser("~/.log_analysis")
    if not os.path.exists(config_file):
        LOG.warning("config file {0} not found".format(config_file))
        sys.exit(1)
    parser.read(config_file)
    if parser.has_section(args.region):

        influxdb_host = read_value(parser, section=args.region, key="influxdb_host")
        influxdb_port = int(read_value(parser, section=args.region, key="influxdb_port"))
        influxdb_user = read_value(parser, section=args.region, key="influxdb_user")
        influxdb_password = read_value(parser, section=args.region, key="influxdb_password")
        influxdb_dbname = read_value(parser, section=args.region, key="influxdb_dbname")

    else:
        sys.exit("Invalid region: '%s'" % args.region)
    influxdb_client = DataFrameClient(host=influxdb_host,
                                      port=influxdb_port,
                                      username=influxdb_user,
                                      password=influxdb_password,
                                      database=influxdb_dbname)
    dbs = influxdb_client.get_list_database()
    create_db = True
    for db in dbs:
        if db['name'] == influxdb_dbname:
            create_db = False
            break
    if create_db:
        influxdb_client.create_database(influxdb_dbname)

    return influxdb_client


def read_statsd_confg():

    config_file = os.path.expanduser("~/.log_analysis")
    if not os.path.exists(config_file):
        LOG.warning("config file {0} not found".format(config_file))
        sys.exit(1)
    parser.read(config_file)
    if parser.has_section(args.region):

        # Statsd
        if parser.has_option("Statsd", 'statshost'):
            statsHost = parser.get("Statsd", 'statshost')
        else:
            statsHost = None
            sys.exit("There is no statshost definition in Statsd section")

        if parser.has_option("Statsd", 'statsPort'):
            statsPort = parser.get("Statsd", 'statsPort')
        else:
            statsPort = None
            sys.exit("There is no statsPort defined in Statsd section")

        if parser.has_option("Statsd", 'statsProject'):
            statsProject = parser.get("Statsd", 'statsProject')
        else:
            statsProject = None
            sys.exit("There is no statsProject definition in Statsd section")
    else:
        sys.exit("Invalid region: '%s'" % args.region)

    stats_client = statsd.StatsClient(statsHost, statsPort, prefix=statsProject)
    return stats_client

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Nginx profiler')
    parser.add_argument('--log', type=str, default='',
                        help='Logfile')
    parser.add_argument('--request_time_threshold', type=int, default=10,
                        help='Threshold to color the row red')
    parser.add_argument('--plot_chart', action='store_true', default=False,
                        help='Plot chart request time x request uri')
    parser.add_argument('--send_to_statsd', action='store_true', default=False,
                        help='Send data to statsd. Need to specify the region too.')
    parser.add_argument('--send_to_influxdb', action='store_true', default=False,
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
        stats_client = read_statsd_confg()

    #infuxdb
    if send_to_influxdb and region:
        influxdb_client = read_influxdb_conf()

    options = {"access_log": access_log,
               "request_time_threshold": request_time_threshold,
               "log_datetime_format": log_datetime_format,
               "plot_chart": plot_chart,
               "uri_white_list": uri_white_list,
               "statsd": statsd,
               "stats_client": stats_client,
               "influxdb_client": influxdb_client}

    sys.exit(0)

    log_analysis = LogAnalysis(options=options)
    log_analysis.run()