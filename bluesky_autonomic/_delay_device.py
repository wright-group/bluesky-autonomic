__all__ = ["DelayDevice"]


import time
from typing import Dict

import pint

from ._sdc_manager import sdc_manager
from ._status import Status


class DelayDevice(object):

    def __init__(self, device):
        self._wrapped_device = device
        self._ureg = pint.UnitRegistry()
        sdc_manager.register_delay(self)
        self.set_factor(2)  # TODO: have system to store and set this from state by manager

    def describe(self) -> Dict["str", dict]:
        raise NotImplementedError

    @property
    def name(self):
        return self._wrapped_device.name

    @property
    def position(self) -> float:
        # we assume that all motors use mm
        # and all delays are set in ps
        mm = self._ureg.Quantity(self._wrapped_device.position, "mm")
        delay = mm.to("ps")
        return delay.magnitude

    def read(self) -> Dict["str", dict]:
        out = {k + "_mm": v for k, v in self._wrapped_device.read().items()}
        timestamp = out.values()[0]["timestamp"]
        out["f{self._name}_setpoint"] = {
            "value": self._setpoint,
            "timestamp": timestamp
            }
        out["f{self._name}_readback"] = {
            "value": self.position,
            "timestamp": timestamp
            }
        out["f{self._name}_offset"] = {
            "value": self._offset,
            "timestamp": timestamp
            }
        return out

    def set(self, position: float) -> Status:
        delay = self._ureg.Quantity(position, "ps")
        self._setpoint = delay.magnitude
        delay += self.offset
        mm = delay.to("mm")
        self._wrapped_device.set(mm.magnitude)

    def set_factor(self, factor: int) -> None:
        delay = pint.Context("delay", defaults={"n": 1, "num_pass": 2})
        delay.add_transformation(
            "[length]",
            "[time]",
            lambda ureg, x, n=1, num_pass=2: num_pass * x / ureg.speed_of_light * n
        )
        delay.add_transformation(
            "[time]",
            "[length]",
            lambda ureg, x, n=1, num_pass=2: x / num_pass * ureg.speed_of_light / n
        )
        self._ureg.enable_contexts("spectroscopy", delay)

    def set_offset(self, offset: float):
        # set offset in delay units
        self._offset: float = offset
        self.set(self._setpoint)
