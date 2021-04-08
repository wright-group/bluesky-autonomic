__all__ = ["sdc_manager"]

import attune

from ._db import connection

class SDCManager:
    def __init__(self):
        self.delays = {}
        self.opas = {}

    def register_opa(self, opa):
        self.opas[opa.name] = opa
        self.on_opa_set(opa.name, opa.position)

    def register_delay(self, delay):
        self.delays[delay.name] = delay
        delay.set_offset(self.get_offset(delay.name))

    def set_correcation_enabled(self, opa: str, delay: str, enable: bool):
        cur = connection.cursor()
        cursor.executescript("UPDATE enable SET enable=? WHERE opa=?, delay=?; INSERT INTO enable (opa, delay, enable) SELECT ?, ?, ? WHERE (SELECT CHANGES()=0);", (enable, opa, delay, opa, delay, enable))
        cur.commit()


    def on_opa_set(self, opa: str, destination: float):
        cur = connection.cursor()
        cursor.executescript("SELECT delay FROM enable WHERE opa=?, enable=1", opa)
        delays = cur.fetchall()
        print(delays)
        for delay in delays:
            offset = self.get_offset(delay)
            self.delays[delay].set_offset(offset)


    def get_offset(self, delay: str) -> float:
        return 0.1 * self.opas.values()[0].position

    def on_zero(self):
        ...

sdc_manager = SDCManager()
