"""Modules."""

from typing import ClassVar

from wg750xxx.modules.module import WagoModule

from .channels import DigitalIn, DigitalOut


class Wg750DigitalOut(WagoModule):
    """750-5xx Digitalausgangsmodul."""

    description: str = "750-5xx Digitalausgangsmodul"
    aliases: ClassVar[list[str]] = ["DO"]
    display_name: ClassVar[str] = "750-5xx"

    # module_spec automatically set by factory
    def create_channels(self) -> None:
        """Create a list of DigitalOut channels for each output channel."""
        for i in range(self.spec.modbus_channels["coil"]):
            self.append_channel(DigitalOut(self.modbus_channels["coil"][i]))


class Wg750DigitalIn(WagoModule):
    """750-4xx Digitaleingangsmodul."""

    description: str = "750-4xx Digitaleingangsmodul"
    aliases: ClassVar[list[str]] = [
        "DI",
        "400",
        "401",
        "405",
        "406",
        "410",
        "411",
        "412",
        "427",
        "438",
    ]
    display_name: ClassVar[str] = "750-4xx"

    # module_spec automatically set by factory
    def create_channels(self) -> None:
        """Create channel implementation."""
        # Create a list of DigitalIn channels for each input channel
        for i in range(self.spec.modbus_channels["discrete"]):
            self.append_channel(DigitalIn(self.modbus_channels["discrete"][i]))
