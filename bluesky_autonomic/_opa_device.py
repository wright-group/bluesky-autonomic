__all__ = ["OPADevice"]


from typing import Dict

from ._sdc_manager import sdc_manager


class OPADevice(object):

    def __init__(self, device):
        self._wrapped_device = device
        sdc_manager.register_opa(self)

    def describe(self) -> Dict["str", dict]:
        raise NotImplementedError

    @property
    def arrangement(self) -> str:
        raise NotImplementedError
