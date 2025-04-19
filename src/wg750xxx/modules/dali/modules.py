"""Dali module."""

from collections.abc import Iterator
from typing import ClassVar, cast

from homeassistant.core import logging

from ..module import WagoModule
from ..spec import IOType, ModbusChannelSpec, ModuleSpec
from .channels import DaliChannel
from .dali_commands import DaliCommands
from .dali_communication import DaliCommunicationRegister

_LOGGER = logging.getLogger(__name__)


class Wg750DaliMaster(WagoModule):
    """750-641 1-Kanal DALI Master."""

    description: str = "750-641 1-Kanal DALI Master"
    aliases: ClassVar[list[str]] = ["641"]
    display_name: ClassVar[str] = "Dali"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True, output=True),
        modbus_channels=ModbusChannelSpec(input=3, holding=3),
    )
    _initialized: bool = False

    # @overrides(MySuperInterface)
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the DALI master.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        """
        super().__init__(*args, **kwargs)
        self.dali_communication_register: DaliCommunicationRegister = (
            DaliCommunicationRegister(self.modbus_connection, self.modbus_address)
        )
        # self.dali_communication_register.read()
        self._initialized = True
        if self.auto_create_channels:
            self.create_channels()
            self.groups: list[DaliChannel] = [
                DaliChannel(address, self.dali_communication_register)
                for address in range(0x40, 0x50)
            ]
            self.all: DaliChannel = DaliChannel(0x3F, self.dali_communication_register)

    def __getitem__(self, key: int) -> DaliChannel | None:
        """Get a DALI channel by index."""
        if self.channel is None:
            return None
        return self.channel[key]

    def __len__(self) -> int:
        """Get the number of DALI channels."""
        if self.channel is None:
            return 0
        return len(self.channel)

    def __iter__(self) -> Iterator[DaliChannel]:
        """Iterate over the DALI channels."""
        if self.channel is None:
            return iter([])
        return iter(cast(list[DaliChannel], self.channel))

    def _read_status_byte(self) -> int:
        """Read the status byte of the DALI message."""
        return self.modbus_channels["input"][0].read_lsb()

    def _write_control_byte(self, value: int) -> None:
        """Write the control byte of the DALI message."""
        self.modbus_channels["holding"][0].write_lsb(value)

    def create_channels(self) -> None:
        """Create the channels of the DALI master."""
        if not self._initialized:
            return
        command = DaliCommands(self.dali_communication_register)
        try:
            short_addresses = command.query_short_address_present()
        except TimeoutError:
            _LOGGER.error(
                "Error setting up DALI channels: Timeout waiting for Dali Response"
            )
            return
        for dali_address in short_addresses:
            self.append_channel(
                DaliChannel(
                    dali_address=dali_address,
                    dali_communication_register=self.dali_communication_register,
                )
            )
