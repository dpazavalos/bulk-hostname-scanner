"""
Side loaded helper modules. Import build, use .new_X_obj on desired object
"""
from ._report_amanager import _RepManFactory, ReporterManagerObj


class _Factory(_RepManFactory):
    """Inheritor of type factories. Init's into 'build' below"""


build = _Factory()
"""Actual importable factory"""
