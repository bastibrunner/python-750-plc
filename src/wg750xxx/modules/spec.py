"""Module specification."""

from dataclasses import dataclass, field
from typing import NamedTuple

from ..modbus.state import ModbusChannelSpec


class IOType(NamedTuple):
    """IO type specification."""

    digital: bool = False
    input: bool = False
    output: bool = False

    def __str__(self) -> str:
        """Get the string representation of the IO type."""
        d = "Digital" if self.digital else ""
        i = "Input" if self.input else ""
        o = "Output" if self.output else ""
        return f"{d}{i}{o}"


@dataclass
class ModuleSpec:
    """Module specification."""

    modbus_channels: ModbusChannelSpec = field(default_factory=dict)
    io_type: IOType = IOType()
    module_type: str = "None"
