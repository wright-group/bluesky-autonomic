"""Support for happi -
pcdshub.github.io/happi
"""


import re
import copy

from happi.item import HappiItem, EntryInfo  # type: ignore


class DelayItem(HappiItem):
    port = EntryInfo("TCP port.", enforce=int, optional=False)
    host = EntryInfo("Host.", optional=True, default="localhost")
    kwargs = copy.copy(HappiItem.kwargs)
    kwargs.default = {"port": "{{port}}", "host": "{{host}}", "name": "{{name}}"}
    device_class = EntryInfo(default="bluesky_autonomic.DelayDevice")


class OPAItem(HappiItem):
    port = EntryInfo("TCP port.", enforce=int, optional=False)
    host = EntryInfo("Host.", optional=True, default="localhost")
    kwargs = copy.copy(HappiItem.kwargs)
    kwargs.default = {"port": "{{port}}", "host": "{{host}}", "name": "{{name}}"}
    device_class = EntryInfo(default="bluesky_autonomic.OPADevice")
