"""Module for handling the channels of a Wago Module."""

import logging
from typing import Any, Literal

from ..settings import ChannelConfig
from ..modbus.state import ModbusChannel

log = logging.getLogger(__name__)

WagoChannelType = Literal[
    "Digital In",
    "Digital Out",
    "Counter 16Bit",
    "Counter 32Bit",
    "Int8 In",
    "Int8 Out",
    "Int16 In",
    "Int16 Out",
    "Float16 In",
    "Float16 Out",
    "Dali",
]


class WagoChannel:
    """Class representing the processed data of a single Channel of a Wago Module.

    Args:
        module: The module the channel belongs to.
        modbus_address: The address of the first channel on the Modbus bus. Should be set on Instance creation.
        channel_type: The type of channel. Just a string to identify the channel type. Should be set on inheriting class.
        channel_count: The number of modbus channels the channel type uses. Should be set on inheriting class.

    Properties:
        module: The module the channel belongs to.
        channel_type: The type of channel. Just a string to identify the channel type.
        modbus_channel: The address offset of the channel relative to the module address.

    """

    platform: str = "sensor"
    device_class: str = "temperature"
    unit_of_measurement: str = "°C"
    icon: str = "mdi:thermometer"
    value_template: str = "{{ value | float }}"

    def __init__(
        self,
        channel_type: Literal[WagoChannelType],
        modbus_channel: ModbusChannel | None = None,
        config: ChannelConfig | None = None,
        channel_index: int | None = None,
    ) -> None:
        """Initialize the channel."""
        self.channel_type: Literal[WagoChannelType] = channel_type
        self.modbus_channel: ModbusChannel | None = modbus_channel
        log.debug("Initializing channel %s", self.__repr__())
        assert self.channel_type is not None, (
            f"channel_type for {self.__class__.__name__} not set"
        )
        self.name: str | None = None
        self.channel_index: int | None = channel_index
        self._config: ChannelConfig = config or ChannelConfig(
            type=self.channel_type,
            platform=self.platform,
            device_class=self.device_class,
            unit_of_measurement=self.unit_of_measurement,
            icon=self.icon,
            value_template=self.value_template,
        )

    def auto_generated_name(self) -> str:
        """Generate a name for the channel."""
        return f"{self.channel_type} {self.channel_index or ''}".rstrip()

    def read(self) -> int | float | bool | None:
        """Read the channel value."""
        raise NotImplementedError(
            f"read method not implemented for {self.__class__.__name__}"
        )

    def write(self, value: Any) -> None:
        """Write the channel value."""
        raise NotImplementedError(
            f"write method not implemented for {self.__class__.__name__}"
        )

    def __str__(self) -> str:
        """Get a string representation of the channel."""
        return f"{self.channel_type} {self.modbus_channel.address}"

    def __repr__(self) -> str:
        """Get a representation of the channel."""
        return (
            f"{self.channel_type} {self.modbus_channel.address} with id {hex(id(self))}"
        )

    def __eq__(self, other: object) -> bool:
        """Check if the channel is equal to another channel."""
        return (
            self.channel_type == other.channel_type
            and self.modbus_channel.address == other.modbus_channel.address
        )

    @property
    def config(self) -> ChannelConfig:
        """Returns a ChannelConfig object."""
        self._config.name = self.name or self.auto_generated_name()
        self._config.type = self.channel_type
        # self._config.index = self.channel_index
        return self._config

    @config.setter
    def config(self, config: ChannelConfig) -> None:
        """Setter for the config."""
        if config.type != self.channel_type:
            raise ValueError(
                f"Channel type {config.type} does not match {self.channel_type}"
            )
        self.name = config.name
        self._config = config
