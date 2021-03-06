__all__ = ["sdc_manager"]

import attune

from ._db import get_connection

class SDCManager:
    def __init__(self):
        self.delays = {}
        self.opas = {}

    def register_opa(self, opa):
        self.opas[opa.name] = opa
        self.on_opa_set(opa.name)

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


    def on_opa_set(self, opa: str):
        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT delay FROM enable WHERE opa=? AND enable=1", (opa,))
        delays = [i[0] for i in cur.fetchall()]
        con.close()

        for delay in delays:
            offset = self.get_offset(delay)
            if delay in self.delays:
                self.delays[delay].set_offset(offset)


    def get_offset(self, delay: str) -> float:
        try:
            instrument = attune.load(f"autonomic_{delay}")
        except:
            instrument = attune.Instrument({}, {}, name=f"autonomic_{delay}")
            attune.store(instrument)

        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT opa FROM enable WHERE delay=? AND enable=1", (delay,))
        enabled = [i[0] for i in cur.fetchall()]
        con.close()

        res = 0
        for k, v in self.opas.items():
            if k in enabled and k in instrument.arrangements and v.arrangement in instrument[k].keys():
                res += instrument[k][v.arrangement](v.position)

        return res

    def on_zero(self, delay):
        try:
            instrument = attune.load(f"autonomic_{delay}")
        except:
            instrument = attune.Instrument({}, {}, name=f"autonomic_{delay}")
            attune.store(instrument)

        for arr in instrument.arrangements:
            if opas[arr].arrangement in instrument[arr].keys():
                instrument = attune.offset_to(instrument, arr, opas[arr].arrangement, 0, opas[arr].position)
        attune.store(instrument)

sdc_manager = SDCManager()
