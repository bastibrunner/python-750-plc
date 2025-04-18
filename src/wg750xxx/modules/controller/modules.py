"""Controller modules."""

from typing import ClassVar

from ..module import WagoModule
from ..spec import IOType, ModbusChannelSpec, ModuleSpec


class Wg750FeldbuskopplerEthernet(WagoModule):
    """Feldbuskoppler Ethernet."""

    description: str = "Feldbuskoppler Ethernet"
    aliases: ClassVar[list[str]] = ["352"]
    display_name: ClassVar[str] = "750-352"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(digital=False, output=False), modbus_channels=ModbusChannelSpec()
    )

    def create_channels(self) -> None:
        """Create channels for the module."""
        # No channels to create for this module
