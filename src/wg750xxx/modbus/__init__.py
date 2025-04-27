"""Modbus package for the wg750xxx module."""

from .exceptions import (
    ModbusCommunicationError,
    ModbusConnectionError,
    ModbusException,
    ModbusProtocolError,
    ModbusTimeoutError,
)
from .state import (
    Coil,
    Discrete,
    Holding,
    Input,
    ModbusChannel,
    ModbusConnection,
    ModbusState,
)

__all__ = [
    "Coil",
    "Discrete",
    "Holding",
    "Input",
    "ModbusChannel",
    "ModbusCommunicationError",
    "ModbusConnection",
    "ModbusConnectionError",
    "ModbusException",
    "ModbusProtocolError",
    "ModbusState",
    "ModbusTimeoutError",
]
