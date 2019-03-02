"""
Side loaded helper modules. Import Adhoc
"""
from ._report_amanager import _RepManFactory


class _Factory(_RepManFactory):
    """Inheritor of type factories. Init's into 'build' below"""


build = _Factory()
"""Actual importable factory"""
