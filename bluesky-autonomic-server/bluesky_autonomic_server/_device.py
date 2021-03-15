__all__ = ["Device"]


from dataclasses import dataclass
from typing import Union


@dataclass
class Device(object):
    name: str
    destination: Union[float, None] = None
    offset: Union[float, None] = None
