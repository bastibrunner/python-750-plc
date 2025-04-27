"""DALI Status Byte."""

from wg750xxx.modbus.registers import Words

from .exceptions import (
    DaliActorError,
    DaliBusError,
    DaliError,
    DaliFrameError,
    DaliGenError,
)


class StatusByte:
    """Class for representing a DALI status byte."""

    def __init__(self) -> None:
        """Initialize the status byte."""
        self._value: int = 0

    @property
    def value(self) -> int:
        """Value of the status byte."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        """Value of the status byte."""
        self._value = value

    @property
    def transmit_accept(self) -> bool:
        """TA: Transmit Accept."""
        return bool(self._value & 0b00000001)

    @transmit_accept.setter
    def transmit_accept(self, value: bool) -> None:
        self._value = (self._value & ~0b00000001) | (value << 0)

    @property
    def receive_request(self) -> bool:
        """RR: Receive Request."""
        return bool(self._value & 0b00000010)

    @receive_request.setter
    def receive_request(self, value: bool) -> None:
        self._value = (self._value & ~0b00000010) | (value << 1)

    @property
    def init_accept(self) -> bool:
        """IA: Init Accept."""
        return bool(self._value & 0b00000100)

    @init_accept.setter
    def init_accept(self, value: bool) -> None:
        self._value = (self._value & ~0b00000100) | (value << 2)

    @property
    def actor_error(self) -> bool:
        """AE: Actor Error."""
        error = bool(self._value & 0b00001000)
        if error:
            raise DaliActorError
        return error

    @actor_error.setter
    def actor_error(self, value: bool) -> None:
        self._value = (self._value & ~0b00001000) | (value << 3)

    @property
    def frame_error(self) -> bool:
        """FE: Frame Error."""
        error = bool(self._value & 0b00010000)
        if error:
            raise DaliFrameError
        return error

    @frame_error.setter
    def frame_error(self, value: bool) -> None:
        self._value = (self._value & ~0b00010000) | (value << 4)

    @property
    def bus_error(self) -> bool:
        """BE: Bus Error."""
        error = bool(self._value & 0b00100000)
        if error:
            raise DaliBusError
        return error

    @bus_error.setter
    def bus_error(self, value: bool) -> None:
        self._value = (self._value & ~0b00100000) | (value << 5)

    @property
    def gen_error(self) -> bool:
        """GE: General Error."""
        error = bool(self._value & 0b01000000)
        if error:
            raise DaliGenError
        return error

    @gen_error.setter
    def gen_error(self, value: bool) -> None:
        self._value = (self._value & ~0b01000000) | (value << 6)

    @property
    def error(self) -> bool:
        """Error."""
        return self.actor_error or self.frame_error or self.bus_error or self.gen_error

    @property
    def register(self) -> Words:
        """Full 6 byte value of the Dali Register."""
        return Words([self.value, 0, 0])

    @register.setter
    def register(self, value: Words) -> None:
        """Set the status byte from a 6 byte register."""
        self._value = value.value[0] & 0xFF
        if self.error:
            raise DaliError

    def __str__(self) -> str:
        """Get a string representation in form of a binary string."""
        return f"{self._value:08b}"

    def __repr__(self) -> str:
        """Get a representation of the status byte."""
        return f"{self._value:08b}"
