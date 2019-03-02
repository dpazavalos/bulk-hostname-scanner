from ._report_zengine import _ReporterEngine


class _SingleCsv(_ReporterEngine):
    """
    Used to export findings to csv report
    """

    def report(self):
        """Cultivates csv report from socket answers"""
        for answer in self._ips.socket_answers:
            # self._sett.csv_sort_by_validity
            pass

        exit("CSV reporting function not yet implemented")
