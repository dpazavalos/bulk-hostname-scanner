from ._report_zengine import _ReporterEngine


class _ReporterManagerObj(_ReporterEngine):
    """
    Reporter Manager object, to be imported and used to call _reporter_caller helper functions
    """

    def __init__(self, constants, settings, ip_report):

        super().__init__(constants=constants, settings=settings, ip_report=ip_report)

        self.reporter_single = None
        """Pointer to single file _reporter_caller object. Imports once needed by report_single"""

        self.reporter_csv = None
        """Pointer to csv _reporter_caller object. Imports once needed by report_csv"""

    def report_single(self):
        """

        :return:
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

        :return:
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

    def __init__(self):
        self._constants = None
        self._settings = None
        self._ip_reports = None

    def _return_repman_obj(self, ):
        return _ReporterManagerObj(self._constants, self._settings, self._ip_reports)
        pass

    def new_reporter_obj(self, constants, settings, ip_report):
        # Pointers to passed data objects
        self._constants = constants
        self._settings = settings
        self._ip_reports = ip_report

        return self._return_repman_obj()
