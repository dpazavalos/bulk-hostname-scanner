from re import search as reg_search
from socket import getfqdn as sock_getfqdn
from typing import Tuple
from ._z_frozen_obj import FrozenObj


class _Constants(FrozenObj):
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    def __init__(self, ):

        self.contacts = 'daniel.avalos@protonmail.com, otherperson@internal.com'
        """Contact emails, to display at the top of the txt report"""

        self.tlds: Tuple[str] = ('', '.com', '.org', '.net', '.gov')
        """Common TLDs. Iterate against each to identify full DNS name"""
        # Substitute internal TLDs once known

        self.known_exclusions: Tuple[str] = ('',
                                             'dnshostname', 'netbios', 'servers', 'server',
                                             'ipaddress', 'ipaddress', 'hostname')
        """known_exclusions: Common report headers; omit these entries\n
        (allows full col copy from reports)"""

        self.rep_file = 'IpBlocks.txt'
        """Output file name"""

        self.local_tld: str = ''
        """localhost's tld, if has one\n
        When not given, DNS will assume similar .domain.TLD . Helpful for figuring IPs,
        but stdout will then only show hostname\n
        Use to check if TLD was assumed, and append to stdout"""
        try:
            self.local_tld += reg_search(r"\..*", sock_getfqdn())[0]
        except TypeError:
            # if local hostname has no TLD, keep as ''
            pass

        # Freeze object
        super().__init__()


class _ConstFactory:
    """Factory method to create new _Constants object"""

    @staticmethod
    def _return_const_obj():
        new_obj = _Constants()
        return new_obj

    def new_const_object(self, ):
        return self._return_const_obj()
