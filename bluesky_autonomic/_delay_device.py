__all__ = ["DelayDevice"]


import time
from typing import Dict

import pint

from ._sdc_manager import sdc_manager
from ._status import Status
from ._db import connection


class DelayDevice(object):

    def __init__(self, device):
        self._wrapped_device = device
        self._ureg = pint.UnitRegistry()
        self.set_factor(2)  # TODO: have system to store and set this from state by manager
        self._offset = 0
        self._zero_position  = 0
        self._setpoint = self.position

        cur = connection.execute("SELECT zero_position FROM delay WHERE delay=?", (self.name,) )
        zero = cur.fetchone()
        if zero is not None:
            self._zero_position = zero[0]
        else:
            self.set_zero(0)

        sdc_manager.register_delay(self)

    def describe(self) -> Dict["str", dict]:
        raise NotImplementedError

    @property
    def name(self):
        return self._wrapped_device.name

    @property
    def position(self) -> float:
        # we assume that all motors use mm
        # and all delays are set in ps
        mm = self._ureg.Quantity(self._wrapped_device.yaq_client.get_position(), "mm")
        mm -= self._ureg.Quantity(self._zero_position, "mm")
        delay = mm.to("ps")
        delay -= self._ureg.Quantity(self._offset, "ps")
        return delay.magnitude

    def read(self) -> Dict["str", dict]:
        out = {k + "_mm": v for k, v in self._wrapped_device.read().items()}
        timestamp = list(out.values())[0]["timestamp"]
        out[f"{self.name}_zero_position"] = {"value": self._zero_position, "timestamp": timestamp}
        out[f"{self.name}_setpoint"] = {
            "value": self._setpoint,
            "timestamp": timestamp
            }
        out[f"{self.name}_readback"] = {
            "value": self.position,
            "timestamp": timestamp
            }
        out[f"{self.name}_offset"] = {
            "value": self._offset,
            "timestamp": timestamp
            }
        return out

    def set(self, position: float) -> Status:
        delay = self._ureg.Quantity(position, "ps")
        self._setpoint = delay.magnitude
        delay += self._ureg.Quantity(self._offset, "ps")
        mm = delay.to("mm")
        mm_with_zero = mm.magnitude+ self._zero_position
        print(f"{self._offset}, {position=}, {delay=}, {mm=}, {mm_with_zero=}")
        return self._wrapped_device.set(mm_with_zero)

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
    
    def set_zero(self, zero: float):
        self._zero_position: float = zero
        self.set(self._setpoint)
        with connection:
            cur = connection.cursor()
            cur.execute("UPDATE delay SET zero_position=? WHERE delay=?", (zero, self.name))
            cur.execute("INSERT INTO delay (delay, zero_position) SELECT ?, ? WHERE (SELECT CHANGES()=0)", (self.name, zero))
        sdc_manager.on_zero(self.name)

