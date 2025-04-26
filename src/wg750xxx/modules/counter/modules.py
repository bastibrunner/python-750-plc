"""Counter modules."""

from typing import ClassVar

from wg750xxx.modules.exceptions import WagoModuleError

from ..module import WagoModule
from ..spec import IOType, ModbusChannelSpec, ModuleSpec
from .channels import Counter32Bit
from .counter_communication import CounterCommunicationRegister


class Wg750Counter(WagoModule):
    """750-404 4-Kanal Zähler."""

    description: str = "750-404 4-Kanal Zähler"
    aliases: ClassVar[list[str]] = ["404", "404_001", "404_004"]
    display_name: ClassVar[str] = "750-404"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True, output=True),
        modbus_channels=ModbusChannelSpec(input=3, holding=3),
    )

    def create_channels(self) -> None:
        """Create channels for the module."""
        if self.modbus_address is None:
            raise WagoModuleError("Can not create channels, modbus address is not set")
        self.append_channel(Counter32Bit(CounterCommunicationRegister(self.modbus_connection, self.modbus_address)))
