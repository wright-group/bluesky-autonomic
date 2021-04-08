__all__ = ["sdc_manager"]

import attune

class SDCManager:
    def __init__(self):
        pass

    def register_device(self, device):
        ...

    def set_correcation_enabled(self, opa, delay, enable):
        ...

    def on_opa_set(self, opa, destination):
        ...

sdc_manager = SDCManager()
