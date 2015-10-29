from __future__ import absolute_import
import unittest
from webserver_log_analysis.parsers.lognit_parser import LognitParser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.lognit_parser = LognitParser()
        self.sample_line_1 = line = 'localhost 2015-10-18 23:59:53 LOCAL6 NOTICE nginx 18/Oct/2015:23:59:53 -0200        127.0.0.1   example.com   GET       /       -       -  -       Local:  400     0       0.000   *383423 Proxy:  -       -       -       -       -       Agent:  -       Fwd:    -'
        self.sample_line_2 = line = 'localhost 2015-10-18 23:59:53 LOCAL6 NOTICE nginx 18/Oct/2015:23:59:53 -0200        127.0.0.1   example.com   POST      //abc//123/       -       -  -       Local:  400     0       0.000   *383423 Proxy:  -       -       -       -       -       Agent:  -       Fwd:    -'
        self.sample_line_3 = line = 'localhost 2015-10-18 23:59:53 LOCAL6 NOTICE nginx 18/Oct/2015:23:59:53 -0200        127.0.0.1   example.com   POST      //abc//123/127.0.0.1/       -       -  -       Local:  400     0       0.000   *383423 Proxy:  -       -       -       -       -       Agent:  -       Fwd:    -'

    def tearDown(self):
        self.lognit_parser = None
        #self.sample_line_1 = None

    def test_filtering_columns(self):

        self.assertEqual('18/Oct/2015:23:59:53 GET / 400 0.000', self.lognit_parser.parse_line(self.sample_line_1))

    def test_filter_double_slashs(self):

        self.assertEqual('18/Oct/2015:23:59:53 POST /abc/#/ 400 0.000', self.lognit_parser.parse_line(self.sample_line_2))

    def test_filter_ip(self):

        self.assertEqual('18/Oct/2015:23:59:53 POST /abc/123/#/ 400 0.000', self.lognit_parser.parse_line(self.sample_line_3))

if __name__ == '__main__':
    unittest.main()