import time
import re
import logging

from . import BasicParser

LOG = logging.getLogger(__name__)

class SampleParser(BasicParser):

    def __init__(self):

        self.columns_to_keep = [6,10,11,16,18] # 0 indexed
        self.reg = re.compile('.*HTTP/1.\d\" (?P<http_status_code>\d{3}) .*')

    def parse_line(self, line):
        # discards unecessary columns
        line = " ".join([line.split()[index] for index in self.columns_to_keep])

if __name__ == "__main__":

    sample_parser = SampleParser()