"""Counter channels."""

from typing import Any

from ..channel import WagoChannel


class Counter16Bit(WagoChannel):
    """Counter 16Bit."""

    platform: str = "number"
    device_class: str = "counter"
    unit_of_measurement: str = ""
    icon: str = "mdi:counter"
    value_template: str = "{{ value | int }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Counter16Bit channel."""
        super().__init__("Counter 16Bit", *args, **kwargs)

    def read(self) -> None:
        """Read the counter value."""
        raise NotImplementedError("read method not implemented for Counter16Bit")


class Counter32Bit(WagoChannel):
    """Counter 32Bit."""

    platform: str = "number"
    device_class: str = "counter"
    unit_of_measurement: str = ""
    icon: str = "mdi:counter"
    value_template: str = "{{ value | int }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Counter32Bit channel."""
        super().__init__("Counter 32Bit", *args, **kwargs)

    def read(self) -> None:
        """Read the counter value."""
        raise NotImplementedError("read method not implemented for Counter32Bit")
