# Webserver log analysis

After pre-processing the log (take a look at the pre-process-log.sh shell script example)
this program uses python's panda lib to provide some analysis, such as, average, min, max, std
request_time for the uris.


# Install

create a virtualenv

    mkvirtualenv webserver-log-analysis
    pip install -r requirements.txt

# TODO

   - Top requests (status code > 200 and < 400)
   - Top errors (status code > 500)

# Sample config file


    [local]
    
    influxdb_host = 192.168.99.100
    influxdb_port = 8086
    influxdb_user = root
    influxdb_password = root
    influxdb_dbname = log_analysis
