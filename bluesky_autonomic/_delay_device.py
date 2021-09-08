__all__ = ["DelayDevice"]


import time
from typing import Dict

import pint
import yaqc_bluesky

from ._sdc_manager import sdc_manager
from ._status import Status
from ._db import get_connection


class DelayDevice(object):

    def __init__(self, port, *, host=None, name=None):
        self.parent = yaqc_bluesky.Device(port=port, host=host, name=name)
        self._ureg = pint.UnitRegistry()
        self.set_factor(2)  # TODO: have system to store and set this from state by manager
        self._offset = 0
        self._zero_position  = 0
        self._setpoint = self.position

        con = get_connection()
        cur = con.execute("SELECT zero_position FROM delay WHERE delay=?", (self.name,) )
        zero = cur.fetchone()
        con.close()
        if zero is not None:
            self._zero_position = zero[0]
        else:
            self.set_zero(0)

        sdc_manager.register_delay(self)

    def describe(self) -> Dict["str", dict]:
        out = {}
        out[f"{self.name}_setpoint"] = {"source": "DelayDevice", "dtype": "number", "shape": [], "units": "ps"}
        out[f"{self.name}_readback"] = {"source": "DelayDevice", "dtype": "number", "shape": [], "units": "ps"}
        out.update({k + "_mm": v for k, v in self.parent.describe().items()})
        out[f"{self.name}_zero_position"] = {"source": "DelayDevice", "dtype": "number", "shape": [], "units": "mm"}
        out[f"{self.name}_offset"] = {"source": "DelayDevice", "dtype": "number", "shape": [], "units": "ps"}
        return out


    @property
    def name(self):
        return self.parent.name

    @property
    def position(self) -> float:
        # we assume that all motors use mm
        # and all delays are set in ps
        mm = self._ureg.Quantity(self.parent.yaq_client.get_position(), "mm")
        mm -= self._ureg.Quantity(self._zero_position, "mm")
        delay = mm.to("ps")
        delay -= self._ureg.Quantity(self._offset, "ps")
        return delay.magnitude

    def read(self) -> Dict["str", dict]:
        out = {}
        timestamp = list(self.parent.read().values())[0]["timestamp"]
        out[f"{self.name}_setpoint"] = {
            "value": self._setpoint,
            "timestamp": timestamp
            }
        out[f"{self.name}_readback"] = {
            "value": self.position,
            "timestamp": timestamp
            }
        out.update({k + "_mm": v for k, v in self.parent.read().items()})
        out[f"{self.name}_zero_position"] = {"value": self._zero_position, "timestamp": timestamp}
        out[f"{self.name}_offset"] = {
            "value": self._offset,
            "timestamp": timestamp
            }
        return out

    def describe_configuration(self) -> Dict["str", dict]:
        return self.parent.describe_configuration()

    def read_configuration(self) -> Dict["str", dict]:
        return self.parent.read_configuration()


    def set(self, position: float) -> Status:
        delay = self._ureg.Quantity(position, "ps")
        self._setpoint = delay.magnitude
        delay += self._ureg.Quantity(self._offset, "ps")
        mm = delay.to("mm")
        mm_with_zero = mm.magnitude+ self._zero_position
        return self.parent.set(mm_with_zero)

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
        con = get_connection()
        with con:
            cur = con.cursor()
            cur.execute("UPDATE delay SET zero_position=? WHERE delay=?", (zero, self.name))
            cur.execute("INSERT INTO delay (delay, zero_position) SELECT ?, ? WHERE (SELECT CHANGES()=0)", (self.name, zero))
        con.close()
        sdc_manager.on_zero(self.name)

    def trigger(self):
        return self.parent.trigger()
