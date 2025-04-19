"""DALI Message."""

import logging
import sys
import time

from wg750xxx.modbus.registers import Words
from wg750xxx.modbus.state import AddressDict, ModbusConnection
from .control_byte import ControlByte
from .exceptions import DaliError
from .status_byte import StatusByte

log = logging.getLogger(__name__)
trace = hasattr(sys, "gettrace") and sys.gettrace() is not None


class DaliInputMessage:
    """DALI Input Message."""

    def __init__(self, register: Words) -> None:
        """Initialize the DALI input message.

        Args:
            register: Words: The register.

        """
        self.dali_response: int = 0
        self.dali_address: int = 0
        self.message_3: int = 0
        self.message_2: int = 0
        self.message_1: int = 0
        self.status_byte: StatusByte = StatusByte()
        self.register: Words = register

    def __eq__(self, other: object) -> bool:
        """Check if the DALI message is equal to another object."""
        if isinstance(other, DaliInputMessage):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self) -> str:
        """Represent the DALI message as a string."""
        return f"{self.__class__.__name__} object at {hex(id(self))}: {self.__dict__}"

    def __str__(self) -> str:
        """Represent the DALI message as a string."""
        return f"{self.__dict__}"

    @property
    def register(self) -> Words:
        """Full 6 byte value of the Dali Register."""
        return Words(
            [
                self.dali_response << 8 | self.status_byte.value,
                self.dali_address | self.message_3 << 8,
                self.message_2 | self.message_1 << 8,
            ]
        )

    @register.setter
    def register(self, words: Words) -> None:
        """Set the DALI message from a 6 byte value."""
        self.status_byte.value = words.value[0] & 0xFF
        self.dali_response = words.value[0] >> 8
        self.dali_address = words.value[1] & 0xFF
        self.message_3 = words.value[1] >> 8
        self.message_2 = words.value[2] & 0xFF
        self.message_1 = words.value[2] >> 8


class DaliOutputMessage:
    """DALI Output Message."""

    def __init__(
        self,
        dali_address: int = 0x00,
        command_code: int | None = None,
        parameter_2: int | None = None,
        parameter_1: int | None = None,
        command_extension: int | None = None,
        brightness: int | None = None,
    ) -> None:
        """Initialize the DALI output message.

        Args:
            dali_address: int: The DALI address.
            command_code: int | None: The command code.
            parameter_2: int | None: The parameter 2.
            parameter_1: int | None: The parameter 1.
            command_extension: int | None: The command extension.
            brightness: int | None: The brightness.

        Raises:
            ValueError: If the command code is None and command_extension is None and brightness is None.

        """
        if command_code is None and command_extension is None and brightness is None:
            raise ValueError(
                "One of command_code or command_extension or brightness must be provided"
            )
        if command_extension is None and (
            parameter_1 is not None or parameter_2 is not None
        ):
            raise ValueError(
                "command_extension must be provided if parameter_1 or parameter_2 is provided"
            )
        self.d0: int = command_code or brightness or 0
        self.d1: int = (dali_address << 1) + (
            brightness is None
        )  # Make YAAAAAAS style register value
        self.d2: int = parameter_2 or 0
        self.d3: int = parameter_1 or 0
        self.d4: int = command_extension or 0
        self.control_byte: ControlByte = ControlByte()

    def __eq__(self, other: object) -> bool:
        """Check if the DALI message is equal to another object."""
        if isinstance(other, DaliInputMessage):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self) -> str:
        """Represent the DALI message as a string."""
        return f"{__class__.__name__} object at {hex(id(self))}: {self.__dict__}"

    def __str__(self) -> str:
        """Represent the DALI message as a string."""
        return f"{self.__dict__}"

    @property
    def register(self) -> Words:
        """Full 6 byte value of the Dali Register."""
        return Words(
            [
                self.d0 << 8 | self.control_byte.value,
                self.d2 << 8 | self.d1,
                self.d4 << 8 | self.d3,
            ]
        )


class DaliCommunicationRegister:
    """Represents the DALI communication registers."""

    def __init__(
        self, modbus_connection: ModbusConnection, modbus_address: AddressDict
    ) -> None:
        """Initialize the DALI communication register.

        Args:
            modbus_connection: ModbusConnection: The modbus connection.
            modbus_address: AddressDict: The modbus address.

        """
        self.modbus_connection = modbus_connection
        self.modbus_address = modbus_address
        self.control_byte: ControlByte = ControlByte()
        self.status_byte: StatusByte = StatusByte()
        self.read_control_byte()
        self.read_status_byte()

    def read_request(self) -> bool:
        """Check if the DALI master is requesting a read."""
        return self.status_byte.receive_request != self.control_byte.receive_accept

    def receive_accept(self) -> None:
        """Receive accept."""
        self.control_byte.receive_accept = self.status_byte.receive_request
        self.modbus_connection.write_registers(
            self.modbus_address["holding"], self.control_byte.register
        )

    def read(self, wait: bool = False) -> DaliInputMessage:
        """Read the DALI message from the modbus channels.

        Args:
            wait: bool: Whether to wait for the receive request bit to be set by the DALI master.

        """
        if wait:
            self.wait_for_receive_request()
        dali_input_message = DaliInputMessage(
            self.modbus_connection.read_input_registers(
                self.modbus_address["input"], 3, True
            )
        )
        self.status_byte = dali_input_message.status_byte
        if self.status_byte.receive_request != self.control_byte.receive_accept:
            self.receive_accept()
        return dali_input_message

    def read_status_byte(self) -> None:
        """Read the status byte from the modbus channels."""
        self.status_byte.value = (
            self.modbus_connection.read_input_register(
                self.modbus_address["input"], True
            )
            & 0xFF
        )

    def read_control_byte(self) -> None:
        """Read the control byte from the modbus channels."""
        self.control_byte.value = (
            self.modbus_connection.read_holding_register(
                self.modbus_address["holding"], True
            )
            & 0xFF
        )

    def write(
        self,
        dali_message: DaliOutputMessage,
        response: bool = False,
        timeout: float = 0.2,
    ) -> DaliInputMessage | None:
        """Write the DALI message.

        Args:
            dali_message: DaliOutputMessage: The DALI message to write.
            response: bool: Whether to wait for a response from the DALI message.
            timeout: float: The timeout for the DALI message.

        Returns:
            DaliInputMessage: The DALI message response.

        """
        self.read_status_byte()
        self.read_control_byte()

        if self.read_request():  # TODO: This is a hack to find out why the DALI master is requesting a read.
            data = self.read()
            log.warning(
                "DALI master is requesting an unexpected read before write: %s", data
            )
            raise DaliError("DALI master is requesting an unexpected read.")

        self.control_byte.transmit_request = not self.status_byte.transmit_accept
        dali_message.control_byte = self.control_byte
        self.modbus_connection.write_registers(
            self.modbus_address["holding"], dali_message.register
        )
        self.wait_for_transmit_accept(timeout)
        if response:
            return self.read(wait=False)
        if self.read_request():  # TODO: This is a hack to find out why the DALI master is requesting a read.
            data = self.read()
            log.warning(
                "DALI master is requesting an unexpected read after writing %s \n Data in register: %s",
                dali_message.register,
                data,
            )
            raise DaliError("DALI master is requesting an unexpected read.")

        return None

    def wait_for_receive_request(self, timeout: float = 0.2) -> None:
        """Wait for the receive request."""
        start_time = time.time()
        timeout = timeout * (10 * trace)  # For debugging
        self.read_status_byte()
        while self.status_byte.receive_request == self.control_byte.receive_accept:
            self.read_status_byte()
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for receive request")

    def wait_for_transmit_accept(self, timeout: float = 0.2) -> None:
        """Wait for the transmit accept."""
        start_time = time.time()
        timeout = timeout * (10 * trace)
        self.read_status_byte()
        while self.status_byte.transmit_accept != self.control_byte.transmit_request:
            self.read_status_byte()
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for transmit accept")

    def __str__(self) -> str:
        """Get a string representation of the DALI communication register."""
        return (
            f"Status: {self.status_byte.register} Control: {self.control_byte.register}"
        )
