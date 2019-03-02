"""
Base engine for managing reporting helper functions
"""
from webbrowser import open as wb_open


class _ReporterEngine:
    """
    Base engine object for reporting helper functions. On first reporting call, load engine.
    Engine side loads specific reporting functions as called

    initialize with pointers to active constants, settings, ip_report reference data objects
    """

    def __init__(self, constants, settings, ip_report, ):

        self._const = constants
        self._sett = settings
        self._ips = ip_report

        self._wb_open = wb_open
        """Helper network wide pointer to webbroser opener"""

