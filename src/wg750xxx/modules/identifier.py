"""Module for Wago 750 ModuleIdentifier."""

from typing import LiteralString, Self

from .spec import IOType, ModbusChannelSpec


class ModuleIdentifier(int):
    """Class representing Wago 750 Module Identifier."""

    def __new__(cls, value: int) -> Self:
        """Create a new module identifier.

        Args:
            value: The value of the module identifier.

        Returns:
            The new module identifier.

        Raises:
            ValueError: If the value is not between 0 and 65535.

        """
        if not 0 <= value <= 0xFFFF:
            raise ValueError(
                f"Module identifier must be between 0 and 65535, got {value}"
            )
        return super().__new__(cls, value)

    def __init__(self, value: int) -> None:
        """Initialize the module identifier.

        Args:
            value: The value of the module identifier.

        Raises:
            ValueError: If the value is not between 0 and 65535.

        """
        self._value = value

    def is_digital(self) -> bool:
        """Get True if the module is digital."""
        return bool(self._value & 0x8000)

    def has_input(self) -> bool:
        """Get True if the module has input channels."""
        if not self.is_digital():
            raise ValueError("Module is not digital")
        return bool(self._value & 0x0001)

    def has_output(self) -> bool:
        """Get True if the module has output channels."""
        if not self.is_digital():
            raise ValueError("Module is not digital")
        return bool(self._value & 0x0002)

    def channel_count(self) -> int:
        """Get the number of channels in the module."""
        if not self.is_digital():
            raise ValueError("Module is not digital")
        return (self._value & 0x7FFF) >> 8

    def io_type(self) -> IOType:
        """Get the IO type of the module."""
        if not self.is_digital():
            raise ValueError("Module is not digital")
        return IOType(digital=True, input=self.has_input(), output=self.has_output())

    def io_channels(self) -> ModbusChannelSpec:
        """Get the IO channel configuration of the module."""
        if not self.is_digital():
            raise ValueError("Module is not digital")
        return ModbusChannelSpec(
            coil=self.has_output() * self.channel_count(),
            discrete=self.has_input() * self.channel_count(),
        )

    def __str__(self) -> LiteralString | str:
        """Get a string representation of the module identifier."""
        if self.is_digital():
            return (
                f"D{'I' if self.has_input() else ''}{'O' if self.has_output() else ''}"
            )
        return str(self._value)
