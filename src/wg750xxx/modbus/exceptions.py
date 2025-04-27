"""Exceptions for the modbus package."""


class ModbusException(Exception):
    """Base exception for the modbus package."""


class ModbusConnectionError(ModbusException):
    """Exception for errors related to the Modbus connection."""


class ModbusTimeoutError(ModbusException):
    """Exception for timeout errors during Modbus operations."""


class ModbusCommunicationError(ModbusException):
    """Exception for communication errors during Modbus operations."""


class ModbusProtocolError(ModbusException):
    """Exception for protocol errors during Modbus operations."""
