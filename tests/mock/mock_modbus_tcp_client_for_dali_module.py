"""Mocked modbus tcp client for testing dali module."""

import logging

from pymodbus.pdu import ModbusPDU

from .mock_modbus_tcp_client import MockModbusPDU, MockModbusTcpClient

# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,unused-argument,too-many-return-statements,unused-variable

log = logging.getLogger(__name__)


class MockModbusTcpClientForDaliModule(MockModbusTcpClient):
    """Mocked modbus tcp client for testing dali module."""

    def __init__(self, modbus_tcp_client_mock) -> None:
        """Initialize the mock modbus tcp client for dali module."""
        log.info("Initializing MockModbusTcpClientForDaliModule")
        super().__init__(modbus_tcp_client_mock, {641: 1})

    def initialize_state(self) -> None:
        """Initialize the state."""
        log.info("Initializing state")
        self._input_registers = [0, 0, 0]  # 3 input registers
        self._holding_registers = [0, 0, 0]  # 3 holding registers
        self._discrete_inputs = []  # 0 discrete inputs
        self._coils = []  # 0 coils

    def read_input_registers(self, address=0, count=2) -> ModbusPDU:
        """Read the input registers."""
        if address >= 0x1000:
            log.debug("Reading special registers >0x1000")
            return super().read_input_registers(address, count)
        log.debug("Reading input registers")
        response = MockModbusPDU()
        response.registers = self._input_registers[address : address + count]
        log.debug("Read input registers: %s", response.registers)
        return response

    def write_registers(self, address, values) -> None:
        """Write the registers."""
        log.debug("Writing registers: %d %s", address, values)
        super().write_registers(address, values)
        if self.transmit_request():
            log.debug("Received transmit request, acknowledging")
            self.acknowledge_transmit_request()
            self.simulate_dali_response()
            log.debug("Updated input registers: %d", self._input_registers[0x0000])

    def transmit_request(self) -> bool:
        """Check if the transmit request bit is set."""
        return (
            self._holding_registers[0x0000] & 0x0001
            != self._input_registers[0x0000] & 0x0001
        )

    def acknowledge_transmit_request(self) -> None:
        """Acknowledge the transmit request."""
        self._input_registers[0x0000] = (
            self._input_registers[0x0000] & 0xFE
            | self._holding_registers[0x0000] & 0x01
        )

    def simulate_dali_response(self) -> None:
        """Execute the dali response."""
        c = self._holding_registers[0x0000] & 0xFF  # least significant byte of r0
        d0 = self._holding_registers[0x0000] >> 8  # most significant byte of r0
        d1 = self._holding_registers[0x0001] & 0xFF  # least significant byte of r1
        d2 = self._holding_registers[0x0001] >> 8  # most significant byte of r1
        d3 = self._holding_registers[0x0002] & 0xFF  # least significant byte of r2
        d4 = self._holding_registers[0x0002] >> 8  # most significant byte of r2

        dali_response = (c, d0, d1, d2, d3, d4)
        log.info("Dali response: %s", dali_response)

        if d4 != 0:
            log.info("Executing Extended Command")
            command = d4
            self.execute_extended_command(command)
        else:
            log.info("Executing Dali Command")
            command = d0

    def execute_extended_command(self, command: int) -> None:
        """Execute the extended command."""
        s = self._input_registers[0x0000] & 0xFF  # least significant byte of r0
        d0 = self._input_registers[0x0000] >> 8  # most significant byte of r0
        d1 = self._input_registers[0x0001] & 0xFF  # least significant byte of r1
        d2 = self._input_registers[0x0001] >> 8  # most significant byte of r1
        d3 = self._input_registers[0x0002] & 0xFF  # least significant byte of r2
        d4 = self._input_registers[0x0002] >> 8  # most significant byte of r2

        match command:
            case 0x06:
                log.info("Executing Query Short Address Present Command 0x06")
                # Bits set for addresses: 2, 7, 10, 14, 18, 21, 26, 28
                # addresses 0-7: bit 2 and bit 7 set -> 0x84 (10000100b)
                # addresses 8-15: bit 2 and bit 6 set -> 0x44 (01000100b)
                # addresses 16-23: bit 2 and bit 5 set -> 0x24 (00100100b)
                # addresses 24-31: bit 2 and bit 4 set -> 0x14 (00010100b)
                d0 = 0b10000100  # addresses 0-7: 2, 7
                d1 = 0x00        # clear
                d2 = 0b01000100  # addresses 8-15: 10, 14
                d3 = 0b00100100  # addresses 16-23: 18, 21
                d4 = 0b00010100  # addresses 24-31: 26, 28
            case 0x07:
                log.info("Executing Query Short Address Present Command 0x07")
                # Bits set for addresses: 32, 36, 40, 45, 48, 54, 56, 63
                # addresses 32-39: bit 0 and bit 4 set -> 0x11 (00010001b)
                # addresses 40-47: bit 0 and bit 5 set -> 0x21 (00100001b)
                # addresses 48-55: bit 0 and bit 6 set -> 0x41 (01000001b)
                # addresses 56-63: bit 0 and bit 7 set -> 0x81 (10000001b)
                d0 = 0b00010001  # addresses 32-39: 32, 36
                d1 = 0x00        # clear
                d2 = 0b00100001  # addresses 40-47: 40, 45
                d3 = 0b01000001  # addresses 48-55: 48, 54
                d4 = 0b10000001  # addresses 56-63: 56, 63

        s = (s | (self._holding_registers[0x0000] & 0x02)) ^ 0x02
        self._input_registers[0x0000] = d0 << 8 | s
        self._input_registers[0x0001] = d2 << 8 | d1
        self._input_registers[0x0002] = d4 << 8 | d3

    def execute_dali_command(self, command: int) -> None:
        """Execute the dali command."""
