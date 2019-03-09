"""
Base engine for managing reporting helper functions
"""
from tempfile import TemporaryFile
from hostname_resolver.custom_datatypes.threaded_file_handler import TFH
from hostname_resolver import reference_data as ref


class _ReporterEngine:
    """
    Base engine object for reporting helper functions. On first reporting call, load engine.
    Engine side loads specific reporting functions as called

    To prevent recursive imports, child objects do not import active engine settings. Pass pointers
    to active reference objects
    """

    def __init__(self, constants, settings, ip_report, ):

        # Passed pointers to reference data objects
        self._const: ref.Constants = constants
        self._sett: ref.Settings = settings
        self._ips: ref.IpReport = ip_report

        self._file_handler = TFH().handle
        self._temporary_file = TemporaryFile
