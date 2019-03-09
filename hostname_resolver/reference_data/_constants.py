"""
Immmutable constant refeence data template. To be imported from higher build factory,
using local _ConstFactory
"""

from typing import Tuple
from re import search as reg_search
from socket import getfqdn as sock_getfqdn
from hostname_resolver.custom_datatypes.frozentemplate import FrozenObj


class Constants(FrozenObj):
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    def __init__(self, ):

        self.contacts = 'daniel.avalos@protonmail.com, otherperson@internal.com'
        """Contact emails, to display at the top of the txt report"""

        self.tlds: Tuple[str] = ('', '.com', '.org', '.net', '.gov', '.local')
        """Common TLDs. Iterate against each to identify full DNS name"""
        # Substitute internal TLDs once known

        self.known_exclusions: Tuple[str] = ('',
                                             'dnshostname', 'netbios', 'servers', 'server',
                                             'ipaddress', 'ipaddress', 'hostname', 'hostnames',
                                             "Root Domain",)
        """known_exclusions: Common report headers; omit these entries\n
        (allows full col copy from reports)"""

        self.local_tld: str = None
        """localhost's tld, if has one\n
        When not given, DNS will assume similar .domain.TLD . Helpful for figuring IPs,
        but stdout will then only show hostname\n
        Use to check if TLD was assumed, and append to stdout"""
        # Note: corporate devices usually have a tld, but personal ones typically dont

        # Freeze object via super init
        super().__init__()

    def find_local_tld(self):
        """
        If a hostname is resolved without a TLD, it is often because
        it's and the running host's TLD are the same. Because this is a conditional factor,
        and because of extra time needed to figure, call on first instance of an assumed tld.
        """
        self.unfreeze_now()

        self.local_tld = ''
        try:
            self.local_tld += reg_search(r"\..*", sock_getfqdn())[0]
        except TypeError:
            # if local hostname has no TLD, keep as ''
            pass

        self.freeze_now()


class _ConstFactory:
    """Factory method to create new _Constants object"""

    @staticmethod
    def _return_const_obj():
        """Return Memory unique Constants object"""
        new_obj = Constants()
        return new_obj

    def new_const_object(self, ):
        """Build and return a new constants data object, ready for use"""
        return self._return_const_obj()
