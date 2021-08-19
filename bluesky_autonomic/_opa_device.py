__all__ = ["OPADevice"]


import time
from typing import Dict

from ._sdc_manager import sdc_manager
from ._status import Status


class OPADevice:

    def __init__(self, device):
        self.parent = device
        yaqclient = self.parent.yaq_client
        for mot in yaqclient.get_setable_names():
            setattr(self, mot, OPAMotor(self, mot))
        sdc_manager.register_opa(self)

    @property
    def arrangement(self) -> str:
        return self.parent.yaq_client.get_arrangement()

    @property
    def instrument(self) -> str:
        return self.parent.yaq_client.get_instrument()

    def describe(self) -> Dict["str", dict]:
        return self.parent.describe()

    def describe_configuration(self) -> Dict["str", dict]:
        return self.parent.describe_configuration()

    def read_configuration(self) -> Dict["str", dict]:
        return self.parent.read_configuration()

    @property
    def name(self):
        return self.parent.name

    @property
    def position(self) -> float:
        return self.parent.yaq_client.get_position()

    def read(self) -> Dict["str", dict]:
        return self.parent.read()

    def set(self, position: float, exceptions=None) -> Status:
        if exceptions:
            self.parent.yaq_client.set_position_except(position, exceptions)
            ret = self.parent._wait_until_still()
        else:
            ret = self.parent.set(position)
        sdc_manager.on_opa_set(self.name)
        # TODO: join delay status to this status
        return ret

    @property
    def hints(self) -> Dict:
        return self.parent.hints

class OPAMotor:

    def __init__(self, device: OPADevice, motor: str):
        self.parent = device.parent
        self._motor = motor
        self.parent = None

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
        return self._motor

    @property
    def position(self) -> float:
        return self.parent.yaq_client.get_setable_positions()[self._motor]

    def read(self) -> Dict["str", dict]:
        return {self.name: {"value": self.position, "timestamp": time.time()}}

    def set(self, position: float) -> Status:
        self.parent.yaq_client.set_setable_positions({self._motor:position})
        return self.parent._wait_until_still()
    
    @property
    def hints(self) -> Dict:
        out: Dict = {}
        out["fields"] = [self.name]
        return out

    def trigger(self) -> Status:
        return self.parent.trigger()
