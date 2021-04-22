__all__ = ["sdc_manager"]

import attune

from ._db import get_connection

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
        con = get_connection()
        with con:
            cur = con.cursor()
            cur.execute("UPDATE enable SET enable=? WHERE opa=? AND delay=?", (enable, opa, delay))
            cur.execute("INSERT INTO enable (opa, delay, enable) SELECT ?, ?, ? WHERE (SELECT CHANGES()=0)", (opa, delay, enable))
        con.close()


    def on_opa_set(self, opa: str, destination: float):
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT delay FROM enable WHERE opa=? AND enable=1", (opa,))
        delays = cur.fetchall()
        con.close()
        if delays:
            delays = delays[0]

        for delay in delays:
            offset = self.get_offset(delay)
            if delay in self.delays:
                self.delays[delay].set_offset(offset)


    def get_offset(self, delay: str) -> float:
        instrument = attune.load(f"autonomic_{delay}")

        con = get_connection()
        cur.execute("SELECT opa FROM enable WHERE delay=? AND enable=1", (delay,))
        enabled = cur.fetchall()
        con.close()

        res = 0
        for k, v in self.opas.items():
            if k in enabled and k in instrument.arrangements and v.arrangement in instrument[k].keys():
                res += instrument(v.position, k)[v.arrangement]

        return res

    def on_zero(self, delay):
        instrument = attune.load(f"autonomic_{delay}")
        for arr in instrument.arrangements:
            if opas[arr].arrangement in instrument[arr].keys():
                instrument = attune.offset_to(instrument, arr, opas[arr].arrangement, 0, opas[arr].position)
        attune.store(instrument)

sdc_manager = SDCManager()
