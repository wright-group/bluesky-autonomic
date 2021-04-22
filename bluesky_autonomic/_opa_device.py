__all__ = ["OPADevice"]


from typing import Dict

from ._sdc_manager import sdc_manager
from ._status import Status


class OPADevice(object):

    def __init__(self, device):
        self._wrapped_device = device
        sdc_manager.register_opa(self)
        self.parent = None

    @property
    def arrangement(self) -> str:
        return self._wrapped_device.yaq_client.get_arrangement()

    def describe(self) -> Dict["str", dict]:
        return self._wrapped_device.describe()

    def describe_configuration(self) -> Dict["str", dict]:
        return self._wrapped_device.describe_configuration()

    def read_configuration(self) -> Dict["str", dict]:
        return self._wrapped_device.read_configuration()

    @property
    def name(self):
        return self._wrapped_device.name

    @property
    def position(self) -> float:
        return self._wrapped_device.yaq_client.get_position()

    def read(self) -> Dict["str", dict]:
        return self._wrapped_device.read()

    def set(self, position: float) -> Status:
        sdc_manager.on_opa_set(self.name, position)
        # TODO: join delay status to this status
        return self._wrapped_device.set(position)
