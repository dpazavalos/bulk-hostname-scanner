"""Storage for dataclass IPReport object/factory, and immutable Reference object"""


class _IpReportDatatype:
    """Generic Storage object for valids, invalids, and valids_split values, to be gen
    and returned by factory IPReports"""

    valids: list
    """IPs of valid Hostnames"""

    invalids: list
    """Hostnames with no IP found"""

    valids_split: list
    """IPs of valid Hostnames, split into sublists by self.split_size"""

    def reset(self):
        """Resets all lists to empty"""
        self.valids.clear()
        self.invalids.clear()
        self.valids_split.clear()


class IPReports:    # pylint: disable=too-few-public-methods
    """IPReports factory. Call .new() to generate default _IpReportDataType object"""
    @staticmethod
    def new() -> _IpReportDatatype:
        """Returns a new inst IPReport instance"""
        return _IpReportDatatype()


class References:
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    def __init__(self, freeze_post_init=True):

        self._frozen = False
        # Enable all class attributes. By default, _freeze enables and locks @end of init

        self.contacts = 'daniel.avalos@protonmail.com, otherperson@internal.com'
        """Contact emails, to display at the top of the txt report"""

        self.tlds = ('', '.com', '.org', '.net', '.gov')
        """Common TLDs. Iterate against each to identify full DNS name"""
        # Substitute internal TLDs once known

        self.known_exclusions = ('',
                                 'dnshostname', 'netbios', 'servers', 'server',
                                 'ipaddress', 'ipaddress', 'hostname')
        """known_exclusions: Common report headers; omit these entries\n
        (allows full col copy from reports)"""

        self.rep_file = 'IpBlocks.txt'

        if freeze_post_init:
            self._frozen = True

    def freeze_now(self):
        self._frozen = True

    def unfreeze(self):
        self._frozen = False

    def __setattr__(self, item, value):
        """Pre 3.7 emulation of frozen dataclasses. Soft mutation prevention"""
        if self._frozen:
            raise SyntaxError("Consider Constants obj immutable, do not modify!")
        self.__dict__[item] = value

    def __delattr__(self, item):
            """Pre 3.7 emulation of frozen dataclasses. Soft mutation prevention"""
            if self._frozen:
                raise SyntaxError("Consider Constants obj immutable, do not modify!")
            del self.__dict__[item]

