__all__ = [
    "BlueskyAutonomicException",
    "InvalidState",
    "UnknownStatusFailure",
    "StatusTimeoutError",
    "WaitTimeoutError",
]


class BlueskyAutonomicException(Exception):
    pass


class InvalidState(RuntimeError, BlueskyAutonomicException):
    """
    When Status.set_finished() or Status.set_exception(exc) is called too late
    """

    ...


class UnknownStatusFailure(BlueskyAutonomicException):
    """
    Generic error when a Status object is marked success=False without details.
    """

    ...


class StatusTimeoutError(TimeoutError, BlueskyAutonomicException):
    """
    Timeout specified when a Status object was created has expired.
    """

    ...


class UseNewProperty(RuntimeError, BlueskyAutonomicException):
    ...


class WaitTimeoutError(TimeoutError, BlueskyAutonomicException):
    """
    TimeoutError raised when we ware waiting on completion of a task.
    This is distinct from TimeoutError, just as concurrent.futures.TimeoutError
    is distinct from TimeoutError, to differentiate when the task itself has
    raised a TimeoutError.
    """

    ...
