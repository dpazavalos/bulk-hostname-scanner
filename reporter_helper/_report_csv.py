from ._report_zengine import _ReporterEngine


class _SingleCsv(_ReporterEngine):
    """
    Used to export findings to csv report
    """

    def report(self):
        exit("CSV reporting function not yet implemented")
