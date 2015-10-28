
class BasicParser(object):
    """Base class for  parsers"""
    def parse_line(self, line):
        """Take a line and do any parsing we need to do. Required for parsers"""
        raise RuntimeError("Implement me!")
