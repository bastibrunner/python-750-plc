"""Module for representing a DALI control byte."""

from ...modbus.registers import Words


class ControlByte:
    """Class for representing a DALI control byte."""

    def __init__(self) -> None:
        """Initialize the control byte."""
        self._value: int = 0

    @property
    def value(self) -> int:
        """Value of the control byte."""
        return self._value

    @value.setter
    def value(self, value: int) -> None:
        self._value = value

    @property
    def transmit_request(self) -> bool:
        """TR: Transmit Request."""
        return bool(self._value & 0b00000001)

    @transmit_request.setter
    def transmit_request(self, value: bool) -> None:
        self._value = (self._value & ~0b00000001) | (value << 0)

    @property
    def receive_accept(self) -> bool:
        """RA: Receive Accept."""
        return bool(self._value & 0b00000010)

    @receive_accept.setter
    def receive_accept(self, value: bool) -> None:
        self._value = (self._value & ~0b00000010) | (value << 1)

    @property
    def init_request(self) -> bool:
        """IR: Init Request."""
        return bool(self._value & 0b00000100)

    @init_request.setter
    def init_request(self, value: bool) -> None:
        self._value = (self._value & ~0b00000100) | (value << 2)

    @property
    def register(self) -> Words:
        """Full 6 byte value of the Dali Register."""
        return Words([self.value, 0, 0])

    def __str__(self) -> str:
        """Get a string representation in form of a binary string."""
        return f"{self._value:08b}"

    def __repr__(self) -> str:
        """Get a representation of the control byte."""
        return f"{self._value:08b}"
