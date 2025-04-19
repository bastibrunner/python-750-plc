"""Basic channels for the Wago 750 series."""

from typing import Any

from wg750xxx.modbus.state import Coil, Discrete
from ..channel import WagoChannel
from ..exceptions import WagoModuleError


class DigitalIn(WagoChannel):
    """Digital Input."""

    platform: str = "binary_sensor"
    device_class: str = "binary_sensor"
    unit_of_measurement: str = ""
    icon: str = "mdi:binary"
    value_template: str = "{{ value | bool }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the digital input channel.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        Raises:
            ValueError: If the modbus_channel is not a Discrete.

        """
        super().__init__("Digital In", *args, **kwargs)
        if not isinstance(self.modbus_channel, Discrete):
            raise TypeError("modbus_channel must be a Discrete")

    def read(self) -> bool:
        """Read the state of the digital input channel."""
        if self.modbus_channel is None:
            raise WagoModuleError(f"Modbus channel not set for {self.name}")
        return self.modbus_channel.read()

    def write(self, value: Any) -> None:
        """Write a value to the digital input channel.

        Raises:
            WagoModuleError: If the channel is an input channel.

        """
        raise WagoModuleError("Can not write to input channel")


class DigitalOut(WagoChannel):
    """Digital Output."""

    platform: str = "switch"
    device_class: str = "switch"
    unit_of_measurement: str = ""
    icon: str = "mdi:binary"
    value_template: str = "{{ value | bool }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the digital output channel.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        Raises:
            ValueError: If the modbus_channel is not a Coil.

        """
        super().__init__("Digital Out", *args, **kwargs)
        if not isinstance(self.modbus_channel, Coil):
            raise TypeError("modbus_channel must be a Coil")

    def write(self, value: Any) -> None:
        """Write a value to the digital output channel."""
        self.modbus_channel.write(value)

    def read(self) -> bool:
        """Read the state of the digital output channel."""
        return self.modbus_channel.read()
