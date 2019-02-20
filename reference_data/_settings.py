"""Data obj and factory for bulk_hostname_resolver running attributes"""

from ._z_frozen_obj import FrozenObj


class _Settings(FrozenObj):
    """Immutable reference data; settings passed from run(). Freezes on set_settings"""

    def __init__(self, ):

        super().__init__(freeze_post_init=False)

    def set_settings(self,
                     split_size=30,
                     report_joiner=',',
                     text_out=True,
                     return_list=False,
                     verbose=True,
                     ):

        self.unfreeze_now()

        # text_out reporting attributes
        self.split_size: int = split_size
        """# to split list of valids into, for potential scan limits"""
        self.report_joiner: str = report_joiner
        """String character used to separate valids return IPs into"""

        # Module running attributes
        '''self.repeating: bool = True
        """Used to keep run loop repeating, typically in conjunction with text_out"""'''
        self.text_out: bool = text_out
        """Bool to display results in a txt file or not
        Also used by prompt to run again (since running again is only used with text_out"""
        self.return_list: bool = return_list
        """Bool to return final results in a nested list\n
        [0] valids (one list, no chunks), [1] invalids"""
        self.verbose = verbose
        """Enables stdout print"""

        self.freeze_now()


class _SettingsFactory:
    """Factory method to create new _Constants object"""

    @staticmethod
    def _return_settings_obj():
        new_obj = _Settings()
        return new_obj

    def new_settings_object(self, ):
        return self._return_settings_obj()
