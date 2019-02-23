from typing import List, Tuple
from collections import namedtuple


class IpReport:

    def __init__(self):

        self.valids: List[str] = []
        """IPs of valid Hostnames"""

        self.invalids: List[str] = []
        """Hostnames with no IP found"""

        self.valids_split: List[List[str]] = []
        """IPs of valid Hostnames, split into sublists by self.split_size"""

        self.hostnames_in: List[str] = []
        """List of given hostnames to resolve"""

        self.socket_answers: List[namedtuple] = []
        """Answers to extended socket calls. Used for persistence against cumulative runs\n
        given: Given hostname used to get socket answer\n
        fqdn: given hostname and tld used successfully\n
        ip: Found IP from fqdn"""

        self.sock_ans = namedtuple('sock_ans',
                                   'given fqdn ip')
        """Schematic for socket_answer named tuples. Build this and add to socket_answers\n
        given: Given hostname used to get socket answer\n
        fqdn: given hostname and tld used successfully\n
        ip: Found IP from fqdn"""

    def reset(self):
        """Resets non persistent storage arrays"""
        self.valids.clear()
        self.invalids.clear()
        self.valids_split.clear()
        self.hostnames_in.clear()

    def reset_all(self):
        """Resets ALL storage arrays. Clean slate"""
        self.reset()
        self.socket_answers.clear()

    
class _IpReportFactory:
    """Factory method to create new IpReport object"""

    @staticmethod
    def _return_ip_report_obj():
        new_obj = IpReport()
        return new_obj

    def new_ip_report_obj(self, ):
        return self._return_ip_report_obj()

