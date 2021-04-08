__all__ = ["OPADevice"]


from ._sdc_manager import sdc_manager


class OPADevice(object):

    @property
    def arrangement(self) -> str:
        raise NotImplementedError
