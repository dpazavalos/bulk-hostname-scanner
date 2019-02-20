"""
Side loaded factory template, used to store and create unique memory ID objects
"""

# from ._z_documentation import IpReportDoc, ConstantsDoc, SettingsDoc
from ._ip_rep import _IpReportFactory
from ._constants import _ConstFactory
from ._settings import _SettingsFactory


'''class IpReport(_z_documentation.IpReportDoc):
    """Externally referencable pointer to type A format documentation.  No functions.
    If doc is properly built, no work needed here"""


class Constants(_z_documentation.ConstantsDoc):
    """Externally referencable pointer to type B format documentation. No functions.
    If doc is properly built, no work needed here"""'''


class _Factory(_IpReportFactory, _ConstFactory, _SettingsFactory):
    """Inheritor of type factories. Init into 'build' below"""


build = _Factory()
"""Actual importable factory"""
