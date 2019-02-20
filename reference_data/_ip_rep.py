from typing import List


class _IpReport:

    def __init__(self):

        self.valids: List[str] = []
        """IPs of valid Hostnames"""

        self.invalids: List[str] = []
        """Hostnames with no IP found"""

        self.valids_split: List[List[str]] = []
        """IPs of valid Hostnames, split into sublists by self.split_size"""

        self.hostnames_in: List[str] = []
        """List of given hostnames to resolve"""

        self.reset()

    def reset(self):
        """Reset all storage arrays"""
        self.valids.clear()
        self.invalids.clear()
        self.valids_split.clear()
        self.hostnames_in.clear()

    
class _IpReportFactory:
    """Factory method to create new _IpReport object"""

    @staticmethod
    def _return_ip_report_obj():
        new_obj = _IpReport()
        return new_obj

    def new_ip_report_obj(self, ):
        return self._return_ip_report_obj()

