"""
Side loaded factory template, used to store and create unique memory ID objects
"""

from _reference_data import _z_documentation
from _reference_data._ip_rep import _IpReportFactory
from _reference_data._constants import _ConstFactory


class IpReport(_z_documentation.IpReportDoc):
    """Externally referencable pointer to type A format documentation.  No functions.
    If doc is properly built, no work needed here"""


class Constants(_z_documentation.ConstantsDoc):
    """Externally referencable pointer to type B format documentation. No functions.
    If doc is properly built, no work needed here"""


class _Factory(_IpReportFactory, _ConstFactory):
    """Inheritor of type factories. Init by below 'build'"""


build = _Factory()
"""Actual importable factory"""
