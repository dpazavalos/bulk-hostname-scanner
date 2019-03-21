"""
Report Manager object. Import Manager, and then call _report_single or report_csb.
Each function imports desired reporting sub-module on demand
"""

from typing import NamedTuple
from ._report_zengine import _ReporterEngine


class _Refer(NamedTuple):
    """
    Named Tuple containing pointers to active reference objects

    Values:
        constants: constants data object. (_const)
        settings: Settings frozen object (_sett)
        ip_report: storage object for list items (_ips)
    """
    constants: None
    settings: None
    ip_report: None


class ReporterManagerObj(_ReporterEngine):
    """
    Reporter Manager object, to be imported and used to call _reporter_caller helper functions
    """

    def __init__(self, ref_obj: _Refer):

        super().__init__(constants=ref_obj.constants,
                         settings=ref_obj.settings,
                         ip_report=ref_obj.ip_report)
        # Reference object items are assigned into engine values

        self._reporter_single = None
        """Pointer to single file _reporter_caller object. Imports once needed by _report_single"""

        self._reporter_csv = None
        """Pointer to csv _reporter_caller object. Imports once needed by _report_csv_sort"""

        self.dict_call = {
            'single': self._report_single,
            'csv_raw': self._report_csv_raw,
            'csv_sort': self._report_csv_sort,
        }
        """Dictionary containing string keys to call appropriate reporting function.
        Call by [index]()

        single: Call Single file reporter \n
        csv_raw: Call CSV reporter, writing as they were gathered \n
        csv_sort: Call CSV reporter, dividing by valid/invalids and alphabetizing
        """

    def _report_single(self):
        """
        Caller to Single file reporter. Imports module on first call
        """
        # Import and build single _reporter_caller object
        from ._report_single_file import _SingleFile
        if not self._reporter_single:
            self._reporter_single = _SingleFile(constants=self._const,
                                                settings=self._sett,
                                                ip_report=self._ips)
        self._reporter_single.report()

    def _report_csv_sort(self):
        """
        Caller to CSV reporter, with sorting=True. Imports module on first call
        """

        # import and build csv _reporter_caller object
        from ._report_csv import _SingleCsv
        if not self._reporter_csv:
            self._reporter_csv = _SingleCsv(constants=self._const,
                                            settings=self._sett,
                                            ip_report=self._ips)

        self._reporter_csv.report(True)

    def _report_csv_raw(self):
        """
        Caller to CSV reporter, with sorting=False. Imports module on first call
        """

        # import and build csv _reporter_caller object
        from ._report_csv import _SingleCsv
        if not self._reporter_csv:
            self._reporter_csv = _SingleCsv(constants=self._const,
                                            settings=self._sett,
                                            ip_report=self._ips)

        self._reporter_csv.report(False)


class _RepManFactory:
    """
    Returns a ReporterMangerobject for use by calling funcion
    """

    @staticmethod
    def _return_repman_obj(ref):
        return ReporterManagerObj(ref)

    def new_reporter_obj(self, constants, settings, ip_report):
        # Pointers to passed data objects
        ref_to_pass = _Refer(constants=constants, settings=settings, ip_report=ip_report)
        return self._return_repman_obj(ref_to_pass)
