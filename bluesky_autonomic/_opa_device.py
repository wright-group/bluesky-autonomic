__all__ = ["OPADevice"]


from typing import Dict

from ._sdc_manager import sdc_manager
from ._status import Status


class OPADevice:

    def __init__(self, device):
        self._wrapped_device = device
        sdc_manager.register_opa(self)
        self.parent = None
        yaqclient = self._wrapped_device.yaq_client
        for mot in yaqclient.get_setable_names():
            setattr(self, mot, OPAMotor(self, mot))

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
        ret = self._wrapped_device.set(position)
        sdc_manager.on_opa_set(self.name)
        # TODO: join delay status to this status
        return ret

    def set_position_except(self, position: float, exceptions=None):
        if exceptions is None:
            exceptions = []
        ret = self._wrapped_device.set_position_except(position, exceptions)
        sdc_manager.on_opa_set(self.name)
        # TODO: join delay status to this status

class OPAMotor:

    def __init__(self, device: OPADevice, motor: str):
        self._wrapped_device = device._wrapped_device
        self._motor = motor
        self.parent = device

    def describe(self) -> Dict["str", dict]:
        return {
                self.name: {"source":f"bluesky-autonomic:{self.name}",
                                    "shape":(),
                                    "dtype": "number",
                                    }
                }


    def describe_configuration(self) -> Dict["str", dict]:
        return {}

    def read_configuration(self) -> Dict["str", dict]:
        return {}

    @property
    def name(self):
        return f"{self._wrapped_device.name}.{self._motor}"

    @property
    def position(self) -> float:
        return self._wrapped_device.yaq_client.get_setable_positions()[self._motor]

    def read(self) -> Dict["str", dict]:
        return {self.name: self.position}

    def set(self, position: float) -> Status:
        return self._wrapped_device.yaq_client.set_setable_positions({self._motor:position})
