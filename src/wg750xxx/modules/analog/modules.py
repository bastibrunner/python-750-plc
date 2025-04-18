"""Analog Modules."""

from typing import ClassVar

from ..module import WagoModule
from ..spec import IOType, ModbusChannelSpec, ModuleSpec
from .channels import Int16In, Int16Out


class Wg750AnalogOut2Ch(WagoModule):
    """1-Kanal Analogausgangsmodul."""

    description: str = "1-Kanal Analogausgangsmodul"
    aliases: ClassVar[list[str]] = [
        "550",
        "552",
        "554",
        "556",
        "560",
        "562",
        "563",
        "585",
    ]
    display_name: ClassVar[str] = "AO2"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(output=True), modbus_channels=ModbusChannelSpec(holding=2)
    )

    def create_channels(self) -> None:
        """Create a list of Int16Out channels for each output channel."""
        for i in range(self.spec.modbus_channels["holding"]):
            self.append_channel(Int16Out(self.modbus_channels["holding"][i]))


class Wg750AnalogOut4Ch(WagoModule):
    """4-Kanal Analogausgangsmodul."""

    description: str = "4-Kanal Analogausgangsmodul"
    aliases: ClassVar[list[str]] = ["553", "555", "557", "559"]
    display_name: ClassVar[str] = "AO4"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(output=True), modbus_channels=ModbusChannelSpec(holding=4)
    )

    def create_channels(self) -> None:
        """Create a list of Int16Out channels for each output channel."""
        for i in range(self.spec.modbus_channels["holding"]):
            self.append_channel(Int16Out(self.modbus_channels["holding"][i]))


### Analog In Modules


class Wg750AnalogIn1Ch(WagoModule):
    """1-Kanal Analogeingangsmodul."""

    description: str = "1-Kanal Analogeingangsmodul"
    aliases: ClassVar[list[str]] = ["491"]
    display_name: ClassVar[str] = "AI1"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True), modbus_channels=ModbusChannelSpec(input=1)
    )

    def create_channels(self) -> None:
        """Create a list of Int16In channels for each input channel."""
        for i in range(self.spec.modbus_channels["input"]):
            self.append_channel(Int16In(self.modbus_channels["input"][i]))


class Wg750AnalogIn2Ch(WagoModule):
    """2-Kanal Analogeingangsmodul."""

    description: str = "2-Kanal Analogeingangsmodul"
    aliases: ClassVar[list[str]] = [
        "452",
        "454",
        "456",
        "461",
        "462",
        "465",
        "466",
        "467",
        "469",
        "472",
        "474",
        "475",
        "476",
        "477",
        "478",
        "479",
        "480",
        "481",
        "483",
        "485",
        "492",
    ]
    display_name: ClassVar[str] = "AI2"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True), modbus_channels=ModbusChannelSpec(input=2)
    )

    def create_channels(self) -> None:
        """Create a list of Int16In channels for each input channel."""
        for i in range(self.spec.modbus_channels["input"]):
            self.append_channel(Int16In(self.modbus_channels["input"][i]))


class Wg750AnalogIn4Ch(WagoModule):
    """4-Kanal Analogeingangsmodul."""

    description: str = "4-Kanal Analogeingangsmodul"
    aliases: ClassVar[list[str]] = ["450", "453", "455", "457", "459", "460", "468"]
    display_name: ClassVar[str] = "AI4"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True), modbus_channels=ModbusChannelSpec(input=4)
    )

    def create_channels(self) -> None:
        """Create a list of Int16In channels for each input channel."""
        for i in range(self.spec.modbus_channels["input"]):
            self.append_channel(Int16In(self.modbus_channels["input"][i]))


class Wg750AnalogIn8Ch(WagoModule):
    """8-Kanal Analogeingangsmodul."""

    description: str = "8-Kanal Analogeingangsmodul"
    aliases: ClassVar[list[str]] = ["451"]
    display_name: ClassVar[str] = "AI8"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True), modbus_channels=ModbusChannelSpec(input=8)
    )

    def create_channels(self) -> None:
        """Create a list of Int16In channels for each input channel."""
        for i in range(self.spec.modbus_channels["input"]):
            self.append_channel(Int16In(self.modbus_channels["input"][i]))
