"""Data object documentations, to be imported by child definitions and factory template init
 references"""

from typing import List, Tuple


class ConstantsDoc:
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    _frozen: bool = False
    "Enable all class attributes. By default, _freeze enables and locks @end of init"

    contacts: str = ''
    """Contact emails, to display at the top of the txt report"""

    tlds: Tuple[str] = ()
    """Common TLDs. Iterate against each to identify full DNS name"""

    known_exclusions = ()
    """known_exclusions: Common report headers; omit these entries\n
    (allows full col copy from reports)"""

    rep_file = ''
    '''Output file name'''

    def freeze_now(self):
        """Enable frozen attribute"""

    def unfreeze(self):
        """Disable frozen attribute"""

    def __setattr__(self, item, value):
        """Pre 3.7 emulation of frozen dataclasses. Soft mutation prevention"""

    def __delattr__(self, item):
        """Pre 3.7 emulation of frozen dataclasses. Soft mutation prevention"""


class IpReportDoc:
    """
    Generic Storage object for valids, invalids, and valids_split values, to be gen
    and returned by factory IPReports
    """

    valids: List[str] = []
    """IPs of valid Hostnames"""

    invalids: List[str] = []
    """Hostnames with no IP found"""

    valids_split: List[List[str]] = []
    """IPs of valid Hostnames, split into sublists by self.split_size"""

    def reset(self):
        """Resets all Ip Report lists to empty"""
