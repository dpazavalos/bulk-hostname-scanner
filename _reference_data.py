"""Storage for dataclass IPReport object/factory, and immutable Reference object"""

from dataclasses import dataclass
from typing import List


@dataclass
class _IpReportDatatype:
    """Generic Storage object for valids, invalids, and valids_split values, to be gen
    and returned by factory IPReports"""
    valids: List[str]
    """IPs of valid Hostnames"""

    invalids: List[str]
    """Hostnames with no IP found"""

    valids_split: List[List[str]]
    """IPs of valid Hostnames, split into sublists by self.split_size"""

    def reset(self):
        """Resets all lists to empty"""
        for data in self.__dict__:
            if isinstance(self.__dict__[data], list):
                self.__dict__[data] = []


class IPReports:    # pylint: disable=too-few-public-methods
    """IPReports factory. Call .new() to generate default _IpReportDataType object"""
    @staticmethod
    def new() -> _IpReportDatatype:
        """Returns a new inst IPReport instance"""
        return _IpReportDatatype(valids=[], invalids=[], valids_split=[])


@dataclass
class References:
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    contacts = 'daniel.avalos@protonmail.com, otherperson@internal.com'
    """Contact emails, to display at the top of the txt report"""

    tlds = ('', '.com', '.org', '.net', '.gov')
    """Common TLDs. Iterate against each to identify full DNS name"""
    # Substitute internal TLDs once known

    known_exclusions = ('', 'dnshostname', 'netbios', 'servers', 'server',
                        'ipaddress', 'ipaddress', 'hostname')
    """known_exclusions: Common report headers; omit these entries\n
    (allows full col copy from reports)"""

    rep_file = 'IpBlocks.txt'
