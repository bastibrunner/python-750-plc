"""Counter channels."""

from typing import Any

from .counter_communication import CounterCommunicationRegister

from ..channel import WagoChannel

class Counter32Bit(WagoChannel):
    """Counter 32Bit."""

    platform: str = "number"
    device_class: str = "counter"
    unit_of_measurement: str = ""
    icon: str = "mdi:counter"
    value_template: str = "{{ value | int }}"

    def __init__(self, communication_register: CounterCommunicationRegister, *args: Any, **kwargs: Any) -> None:
        """Initialize the Counter32Bit channel."""
        self.communication_register: CounterCommunicationRegister = communication_register
        super().__init__("Counter 32Bit", *args, **kwargs)

    def read(self) -> None:
        """Read the counter value."""
        return self.communication_register.value

    def write(self, value: int) -> None:
        """Write the counter value."""
        raise NotImplementedError("Write method not implemented for Counter32Bit")


    def reset(self) -> None:
        """Reset the counter."""
        self.communication_register.value = 0

    def lock(self) -> None:
        """Lock the counter."""
        self.communication_register.lock = True

    def unlock(self) -> None:
        """Unlock the counter."""
        self.communication_register.lock = False

    def set(self,value:int) -> None:
        """Set the counter."""
        self.communication_register.value = value

    def clear(self) -> None:
        """Clear the counter."""
        self.communication_register.set = False
