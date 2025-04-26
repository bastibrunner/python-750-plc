# pylint: disable=unused-variable,too-many-public-methods
"""Dali channel."""

from typing import Any

from wg750xxx.modules.dali.channel_setup import DaliChannelSetup

from ..channel import WagoChannel
from .channel_commands import DaliChannelCommands
from .channel_status import DaliChannelStatus
from .dali_communication import DaliCommunicationRegister


class DaliChannel(DaliChannelCommands, WagoChannel):
    """Dali channel.

    This class represents a Dali channel with all its functionality.

    Class methods:
    - get_channels: classmethod: Get all Dali channels from the dali master.

    Class properties:
    - dali_address: int: The Dali address of the channel.

    """

    platform: str = "light"
    device_class: str = "brightness"
    unit_of_measurement: str = "%"
    icon: str = "mdi:brightness"
    value_template: str = "{{ value | int}}"

    def __init__(
        self,
        dali_address: int,
        dali_communication_register: DaliCommunicationRegister,
        **kwargs: Any,
    ) -> None:
        """Initialize the Dali channel."""
        self.dali_address = dali_address
        self.channel_type = "Dali"
        super().__init__(
            dali_address=dali_address,
            dali_communication_register=dali_communication_register,
            channel_type=self.channel_type,
            **kwargs,
        )
        self.status: DaliChannelStatus = DaliChannelStatus(self.dali_address, self.dali_communication_register)
        self.setup: DaliChannelSetup = DaliChannelSetup(self.dali_address, self.dali_communication_register)
        self.commands: DaliChannelCommands = DaliChannelCommands(self.dali_address, self.dali_communication_register)

    @property
    def brightness(self) -> int:
        """Get the brightness value."""
        return self.commands.get_current_value()

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Set the brightness value."""
        self.commands.set_brightness(value)

    def read(self, update: bool = False) -> int:
        """Read the brightness value of the Dali channel."""
        if update:
            pass  # Update has no effect on Dali since we always read the value from the bus
        return self.brightness

    def write(self, value: int, update: bool = False) -> None:
        """Write the brightness value to the Dali channel."""
        if update:
            pass  # Update has no effect on Dali since we always write the value directly to the bus
        self.brightness = value

    def __str__(self) -> str:
        """Get a string representation of the Dali channel."""
        return f"{self.channel_type} {self.dali_address}"

    def __repr__(self) -> str:
        """Get a representation of the Dali channel."""
        return f"{self.__class__} object with id {hex(id(self))} ({self.channel_type} {self.dali_address})"
