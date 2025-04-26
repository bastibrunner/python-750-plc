"""Module for handling the channels of a Wago Module."""

import logging
from typing import Any, Literal, Callable, Self

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
        on_change_callback: Callable[[Any], None] | None = None,
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
        self._on_change_callback: Callable[[Any], None] | None = on_change_callback

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

    def get_instance(self) -> Self:
        """Get an instance of the channel."""
        return self

    def __str__(self) -> str:
        """Get a string representation of the channel."""
        if self.modbus_channel is None:
            return f"{self.channel_type} (no modbus address)"
        else:
            return f"{self.channel_type} {self.modbus_channel.address}"

    def __repr__(self) -> str:
        """Get a representation of the channel."""
        if self.modbus_channel is None:
            return f"{self.channel_type} (no modbus address)"
        return (
            f"{self.channel_type} {self.modbus_channel.address} with id {hex(id(self))}"
        )

    def __eq__(self, other: object) -> bool:
        """Check if the channel is equal to another channel."""
        if not isinstance(other, WagoChannel):
            return False
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

    @property
    def on_change_callback(self) -> Callable[[Any], None] | None:
        """Get the callback function that gets called when the channel value changes."""
        return self._on_change_callback

    @on_change_callback.setter
    def on_change_callback(self, callback: Callable[[Any], None] | None) -> None:
        """Set the callback function that gets called when the channel value changes."""
        self._on_change_callback = callback

        # If we have a modbus channel and a valid callback, register with ModbusConnection
        if self.modbus_channel is not None and callback is not None:
            if hasattr(self.modbus_channel, 'modbus_connection') and hasattr(self.modbus_channel.modbus_connection, 'register_channel_callback'):
                self.modbus_channel.modbus_connection.register_channel_callback(self.modbus_channel, self)
        elif self.modbus_channel is not None and callback is None:
            # Unregister if callback is set to None
            if hasattr(self.modbus_channel, 'modbus_connection') and hasattr(self.modbus_channel.modbus_connection, 'unregister_channel_callback'):
                self.modbus_channel.modbus_connection.unregister_channel_callback(self.modbus_channel, self)

    def notify_value_change(self, new_value: Any) -> None:
        """Notify the channel that its value has changed."""
        if self._on_change_callback is not None:
            self._on_change_callback(new_value)
