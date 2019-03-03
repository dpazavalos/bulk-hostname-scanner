"""
Side loaded factory template, used to store and create unique memory ID objects
"""

from ._ip_rep import _IpReportFactory, IpReport, SocketAnswer
from ._constants import _ConstFactory, Constants
from ._settings import _SettingsFactory, Settings


class _Factory(_IpReportFactory, _ConstFactory, _SettingsFactory):
    """Inheritor of type factories. Init into 'build' below"""


build = _Factory()
"""Actual importable factory"""
