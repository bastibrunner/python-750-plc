"""Exceptions for the DALI module."""


class DaliError(Exception):
    """DALI error."""


class DaliActorError(DaliError):
    """DALI actor error."""


class DaliFrameError(DaliError):
    """DALI frame error."""


class DaliBusError(DaliError):
    """DALI bus error."""


class DaliGenError(DaliError):
    """DALI gen error."""
