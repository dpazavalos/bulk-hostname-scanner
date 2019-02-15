from ._z_documentation import IpReportDoc


class _IpReport(IpReportDoc):

    def __init__(self):
        self.reset()

    def reset(self):
        self.valids.clear()
        self.invalids.clear()
        self.valids_split.clear()

    
class _IpReportFactory:
    """Factory method to create new _IpReport object"""

    @staticmethod
    def _return_ip_report_obj():
        new_obj = _IpReport()
        return new_obj

    def _new_ip_report_obj(self, ):
        return self._return_ip_report_obj()

