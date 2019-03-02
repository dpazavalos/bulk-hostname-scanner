"""Data obj and factory for bulk_hostname_resolver running attributes"""

from ._z_frozen_obj import FrozenObj


class Settings(FrozenObj):
    """Immutable reference data; settings passed from run(). Freezes on set_settings"""

    verbose: bool
    """Enables stdout print"""
    sngl_split_size: int
    """# to split list of valids into, for potential scan limits"""
    sngl_report_joiner: str
    """String character used to separate valids return IPs into"""
    csv_sort_by_validity: bool
    """Sort CSV entries by validity"""

    def __init__(self, ):
        super().__init__()

    def set_settings(self, verbose: bool,
                     sngl_split_size: int,
                     sngl_report_joiner: str,
                     csv_sort_by_validity: bool
                     ):
        self.unfreeze_now()

        self.verbose = verbose
        self.sngl_split_size = sngl_split_size
        self.sngl_report_joiner = sngl_report_joiner
        self.csv_sort_by_validity = csv_sort_by_validity

        self.freeze_now()


class _SettingsFactory:
    """Factory method to create new _Constants object"""

    @staticmethod
    def _return_settings_obj():
        new_obj = Settings()
        return new_obj

    def new_settings_object(self, ):
        return self._return_settings_obj()
