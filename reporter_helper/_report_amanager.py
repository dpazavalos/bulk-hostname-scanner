"""
Report Manager object. Import Manager, and then call report_single or report_csb.
Each function imports desired reporting sub-module on demand
"""

from ._report_zengine import _ReporterEngine
from typing import NamedTuple


class _Ref(NamedTuple):
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

    def __init__(self, ref_obj: _Ref):

        super().__init__(constants=ref_obj.constants,
                         settings=ref_obj.settings,
                         ip_report=ref_obj.ip_report)
        # Reference object items are assigned into engine values

        self.reporter_single = None
        """Pointer to single file _reporter_caller object. Imports once needed by report_single"""

        self.reporter_csv = None
        """Pointer to csv _reporter_caller object. Imports once needed by report_csv"""

    def report_single(self):
        """
        Caller to Single file reporter. Imports module on first call
        """
        # Import and build single _reporter_caller object
        from ._report_single_file import _SingleFile
        if not self.reporter_single:
            self.reporter_single = _SingleFile(constants=self._const,
                                               settings=self._sett,
                                               ip_report=self._ips)
        self.reporter_single.report()

    def report_csv(self):
        """
        Caller to CSV reporter. Imports module on first call
        """

        # import and build csv _reporter_caller object
        from ._report_csv import _SingleCsv
        if not self.reporter_csv:
            self.reporter_csv = _SingleCsv(constants=self._const,
                                           settings=self._sett,
                                           ip_report=self._ips)

        self.reporter_csv.report()


class _RepManFactory:
    """
    Returns a ReporterMangerobject for use by calling funcion
    """

    @staticmethod
    def _return_repman_obj(ref):
        return ReporterManagerObj(ref)
        pass

    def new_reporter_obj(self, constants, settings, ip_report):
        # Pointers to passed data objects
        ref_to_pass = _Ref(constants=constants, settings=settings, ip_report=ip_report)
        return self._return_repman_obj(ref_to_pass)
