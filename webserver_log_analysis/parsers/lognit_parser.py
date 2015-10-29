import time
import re
import logging
from webserver_log_analysis.parsers import BasicParser

LOG = logging.getLogger(__name__)

class LognitParser(BasicParser):
    """

    #filter replace id for #
    sed -i "s@/[0-9]\{1,9\}[/]@/#/@g" ${FILENAME}.preprocessed

    #filter replace uris ending with id without slash for #
    sed -i "s@/[0-9]\{1,9\}[ ]@/#/ @g" ${FILENAME}.preprocessed

    #filter uuid
    sed -i 's/[a-fA-F0-9]\{8\}-[a-fA-F0-9]\{4\}-4[a-fA-F0-9]\{3\}-[89aAbB][a-fA-F0-9]\{3\}-[a-fA-F0-9]\{12\}/UUID/g' ${FILENAME}.preprocessed

    """

    def __init__(self):

        self.columns_to_keep = [6,10,11,16,18] # 0 indexed
        self.reg = re.compile('.*HTTP/1.\d\" (?P<http_status_code>\d{3}) .*')
        # patterns is list with tuples, containing the regexp and the replacement string
        # \/[0-9]{1,9}[^.:]
        self.patterns = [("//","/"),
                         ("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", "#"),
                         ("/[0-9]{1,9}/", "/#/"),
                         ("/[0-9]{1,9} ", "/# "),]


    def parse_line(self, line):
        # discards unecessary columns
        line = " ".join([line.split()[index] for index in self.columns_to_keep])

        for pattern in self.patterns:
            reg = re.compile(pattern[0])
            matches = reg.findall(line)
            if matches:
                line = reg.sub(pattern[1], line)

        return line

if __name__ == "__main__":

    sample_parser = LognitParser()