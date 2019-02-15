from ._z_documentation import ConstantsDoc


class _Constants(ConstantsDoc):
    """Immutable reference data; contact info, known TLDs, known exclusions"""

    def __init__(self, freeze_post_init=True):

        self.contacts += 'daniel.avalos@protonmail.com, otherperson@internal.com'

        self.tlds += ('', '.com', '.org', '.net', '.gov')
        # Substitute internal TLDs once known

        self.known_exclusions += ('',
                                  'dnshostname', 'netbios', 'servers', 'server',
                                  'ipaddress', 'ipaddress', 'hostname')

        self.rep_file += 'IpBlocks.txt'

        if freeze_post_init:
            self._frozen = True

    def freeze_now(self):
        self._frozen = True

    def unfreeze(self):
        self.__dict__['_frozen'] = False

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


class _ConstFactory:
    """Factory method to create new _Constants object"""

    @staticmethod
    def _return_const_obj():
        new_obj = _Constants()
        return new_obj

    def new_const_object(self, ):
        return self._return_const_obj()
