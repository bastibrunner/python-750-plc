"""Basic channels for the Wago 750 series."""

from typing import Any, Literal

from ..channel import WagoChannel
from ..exceptions import WagoModuleError

BytePosition = Literal["MSB", "LSB"]


class Int16In(WagoChannel):
    """16-Bit Analog Input Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | int }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Int16In channel."""
        super().__init__("Int16 In", *args, **kwargs)

    def read(self) -> int | None:
        """Read the value of the channel."""
        if self.modbus_channel is None:
            return None
        return self.modbus_channel.read()

    def write(self, value: Any) -> None:
        """Write a value to the channel."""
        raise WagoModuleError("Can not write to input channel")


class Int16Out(WagoChannel):
    """16-Bit Analog Output Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | int }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Int16Out channel."""
        super().__init__("Int16 Out", *args, **kwargs)

    def write(self, value: Any) -> None:
        """Write a value to the channel."""
        if self.modbus_channel is None:
            raise WagoModuleError(f"Modbus channel not set for {self.name}")
        self.modbus_channel.write(value)

    def read(self) -> int:
        """Read the value of the channel."""
        if self.modbus_channel is None:
            raise WagoModuleError(f"Modbus channel not set for {self.name}")
        return self.modbus_channel.read()


class Int8In(WagoChannel):
    """8-Bit Analog Input Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | int }}"

    def __init__(self, byte_position: BytePosition, *args: Any, **kwargs: Any) -> None:
        """Initialize the Int8In channel."""
        super().__init__("Int8 In", *args, **kwargs)
        self.byte_position = byte_position

    def read(self) -> int:
        """Read the value of the channel."""
        if self.modbus_channel is None:
            raise WagoModuleError(f"Modbus channel not set for {self.name}")
        return (
            self.modbus_channel.read_lsb()
            if self.byte_position == "LSB"
            else self.modbus_channel.read_msb()
        )

    def write(self, value: Any) -> None:
        """Write a value to the channel."""
        raise WagoModuleError("Can not write to input channel")


class Int8Out(WagoChannel):
    """8-Bit Analog Output Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | int }}"

    def __init__(self, byte_position: BytePosition, *args: Any, **kwargs: Any) -> None:
        """Initialize the Int8Out channel."""
        super().__init__("Int8 Out", *args, **kwargs)
        self.byte_position = byte_position

    def write(self, value: int) -> None:
        """Write a value to the channel."""
        assert isinstance(value, int) and 0 <= value <= 255, (
            "Value must be an integer between 0 and 255"
        )
        if self.byte_position == "LSB":
            self.modbus_channel.write_lsb(value)
        else:
            self.modbus_channel.write_msb(value)

    def read(self) -> int:
        """Read the value of the channel."""
        return (
            self.modbus_channel.read_lsb()
            if self.byte_position == "LSB"
            else self.modbus_channel.read_msb()
        )


class Float16In(WagoChannel):
    """Float16 Input Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | float }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Float16In channel."""
        super().__init__("Float16 In", *args, **kwargs)

    def read(self) -> float:
        """Read the value of the channel."""
        return self.modbus_channel.read()

    def write(self, value: Any) -> None:
        """Write a value to the channel."""
        raise WagoModuleError("Can not write to input channel")


class Float16Out(WagoChannel):
    """Float16 Output Channel."""

    platform: str = "number"
    device_class: str = "number"
    unit_of_measurement: str = ""
    icon: str = ""
    value_template: str = "{{ value | float }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Float16Out channel."""
        super().__init__("Float16 Out", *args, **kwargs)

    def write(self, value: float) -> None:
        """Write a value to the channel."""
        self.modbus_channel.write(value)

    def read(self) -> float:
        """Read the value of the channel."""
        return self.modbus_channel.read()
