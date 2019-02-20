"""Data object documentations, to be imported by child definitions and factory template init
 references"""

from typing import List, Tuple
from ._z_frozen_obj import FrozenObj


class SettingsDoc(FrozenObj):
    """Settings object for bulk_hostname_resolver running attributes"""

    # text_out reporting attributes
    split_size = 30
    """# to split list of valids into, for potential scan limits"""

    report_joiner = ','
    """String character used to separate valids return IPs into"""

    # Module running attributes
    repeating = True
    """Used to keep run loop repeating, typically in conjunction with text_out"""

    text_out = True
    """Bool to display results in a txt file or not
    Also used by prompt to run again (since running again is only used with text_out"""

    return_list = False
    """Bool to return final results in a nested list\n
    [0] valids (one list, no chunks), [1] invalids"""

    verbose = True
    """Enables stdout progress print"""


class ConstantsDoc(FrozenObj):
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    contacts: str = ''
    """Contact emails, to display at the top of the txt report"""

    tlds: Tuple[str] = ()
    """Common TLDs. Iterate against each to identify full DNS name"""

    known_exclusions = ()
    """known_exclusions: Common report headers; omit these entries\n
    (allows full col copy from reports)"""

    rep_file = ''
    '''Output file name'''


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

    hostnames_in: List[str] = []
    """List of given hostnames to resolve"""

    def reset(self):
        """Resets all Ip Report lists to empty"""
