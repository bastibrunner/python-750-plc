"""Mocked modbus tcp client for testing."""

import logging
from random import randint, sample

from pymodbus.pdu import ModbusPDU

log = logging.getLogger(__name__)


class MockModbusPDU(ModbusPDU):
    """Concrete implementation of ModbusPDU for testing."""

    def encode(self) -> bytes:
        """Encode the data."""
        return b""

    def decode(self, data: bytes) -> None:
        """Decode the data."""


# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,unused-argument,too-many-return-statements


class MockModbusTcpClient:
    """Mocked modbus tcp client for testing."""

    module_configs: dict[str, dict[int, int]] = {
        "input_registers": {459: 4, 453: 4, 460: 4, 451: 8, 404: 3, 641: 3},
        "holding_registers": {559: 4, 404: 3, 641: 3},
        "discrete_inputs": {36865: 16, 33793: 4, 33281: 2},
        "coils": {33794: 4, 36866: 16},
    }

    def __init__(
        self, modbus_tcp_client_mock, modules: dict[int, int] | None = None
    ) -> None:
        """Initialize the mock modbus tcp client."""
        log.info("Initializing MockModbusTcpClient")
        self._input_registers: list[int] = []
        self._holding_registers: list[int] = []
        self._discrete_inputs: list[bool] = []
        self._coils: list[bool] = []

        if modules is not None:
            self.modules = modules
        else:
            log.info("No modules provided, using default modules")
            self.modules = {
                352: 1,
                559: 1,
                33794: 1,
                36866: 1,
                36865: 1,
                33793: 1,
                459: 1,
                453: 1,
                460: 1,
                451: 1,
                404: 1,
                33281: 1,
            }

        log.info("Modules: %s", self.modules)
        self.modbus_tcp_client_mock = modbus_tcp_client_mock
        self.modbus_tcp_client_mock.return_value.connect.return_value = True
        self.modbus_tcp_client_mock.return_value.read_input_registers.side_effect = (
            self.read_input_registers
        )
        self.modbus_tcp_client_mock.return_value.read_holding_registers.side_effect = (
            self.read_holding_registers
        )
        self.modbus_tcp_client_mock.return_value.read_discrete_inputs.side_effect = (
            self.read_discrete_inputs
        )
        self.modbus_tcp_client_mock.return_value.read_coils.side_effect = (
            self.read_coils
        )
        self.modbus_tcp_client_mock.return_value.write_coils.side_effect = (
            self.write_coils
        )
        self.modbus_tcp_client_mock.return_value.write_registers.side_effect = (
            self.write_registers
        )
        self.modbus_tcp_client_mock.return_value.write_coil.side_effect = (
            self.write_coil
        )
        self.modbus_tcp_client_mock.return_value.write_register.side_effect = (
            self.write_register
        )
        self.initialize_state()

    def initialize_state(self) -> None:
        """Initialize the state of the mock modbus tcp client."""
        self.randomize_state()

    def randomize_state(self) -> None:
        """Randomize the state of the mock modbus tcp client."""
        log.info("Initializing state with random values")
        self._input_registers = sample(
            range(1, 0xFFFF),
            sum(
                self.modules.get(module_id, 0) * register_count
                for module_id, register_count in self.module_configs[
                    "input_registers"
                ].items()
            ),
        )
        log.info("Input registers: %s", self._input_registers)
        self._holding_registers = sample(
            range(1, 0xFFFF),
            sum(
                self.modules.get(module_id, 0) * register_count
                for module_id, register_count in self.module_configs[
                    "holding_registers"
                ].items()
            ),
        )
        log.info("Holding registers: %s", self._holding_registers)
        self._discrete_inputs = [
            bool(randint(0, 1))
            for _ in range(
                sum(
                    self.modules.get(module_id, 0) * register_count
                    for module_id, register_count in self.module_configs[
                        "discrete_inputs"
                    ].items()
                )
            )
        ]
        log.info("Discrete inputs: %s", self._discrete_inputs)
        self._coils = [
            bool(randint(0, 1))
            for _ in range(
                sum(
                    self.modules.get(module_id, 0) * register_count
                    for module_id, register_count in self.module_configs[
                        "coils"
                    ].items()
                )
            )
        ]
        log.info("Coils: %s", self._coils)

    def set_state(
        self,
        input_registers: list[int] | None = None,
        holding_registers: list[int] | None = None,
        discrete_inputs: list[bool] | None = None,
        coils: list[bool] | None = None,
    ) -> None:
        """Set the state of the mock modbus tcp client."""
        if input_registers is not None:
            self._input_registers = input_registers
        if holding_registers is not None:
            self._holding_registers = holding_registers
        if discrete_inputs is not None:
            self._discrete_inputs = discrete_inputs
        if coils is not None:
            self._coils = coils

    def read_input_registers(self, address=0, count=2) -> ModbusPDU:
        """Read input registers."""
        response = MockModbusPDU()
        if address == 0x1022:
            # count of analog outputs
            log.info("Reading count of analog outputs")
            response.registers = [len(self._holding_registers) * 16]
        elif address == 0x1023:
            # count of analog inputs
            log.info("Reading count of analog inputs")
            response.registers = [len(self._input_registers) * 16]
        elif address == 0x1024:
            # count of digital outputs
            log.info("Reading count of digital outputs")
            response.registers = [len(self._coils)]
        elif address == 0x1025:
            # count of digital inputs
            log.info("Reading count of digital inputs")
            response.registers = [len(self._discrete_inputs)]
        elif address == 0x2030:
            # 64 Module IDs
            log.info("Reading 64 Module IDs")
            response.registers = list(self.modules.keys()) + [0] * (
                64 - len(self.modules)
            )
        elif address in {0x2031, 0x2032}:
            # (next) 64 Module IDs
            log.info("Reading (next) 64 Module IDs")
            response.registers = [0] * 64
        elif address == 0x2010:
            # REVISION
            log.info("Reading REVISION")
            response.registers = [1]
        elif address == 0x2011:
            # SERIES
            log.info("Reading SERIES")
            response.registers = [750]
        elif address == 0x2012:
            # ITEM
            log.info("Reading ITEM")
            response.registers = [1]
        elif address == 0x2013:
            # FW_VERS major
            log.info("Reading FW_VERS major")
            response.registers = [1]
        elif address == 0x2014:
            # FW_VERS minor
            log.info("Reading FW_VERS minor")
            response.registers = [0]
        elif address == 0x2021:
            # FW_TIMESTAMP date
            log.info("Reading FW_TIMESTAMP date")
            response.registers = [ord(c) for c in "2024-03-21".ljust(8, "\0")][:count]
        elif address == 0x2022:
            # FW_TIMESTAMP time
            log.info("Reading FW_TIMESTAMP time")
            response.registers = [ord(c) for c in "12:00:00".ljust(8, "\0")][:count]
        elif address == 0x2023:
            # FW_INFO
            log.info("Reading FW_INFO")
            response.registers = [ord(c) for c in "Mock Firmware".ljust(32, "\0")][
                :count
            ]
        else:
            log.info("Reading input registers from %d to %d", address, address + count)
            response.registers = self._input_registers[address : address + count]
        return response

    def read_holding_registers(self, address=0, count=1) -> ModbusPDU:
        """Read holding registers."""
        log.info("Reading holding registers from %d to %d", address, address + count)
        if address >= 0x200:
            address -= 0x200
        response = MockModbusPDU()
        response.registers = self._holding_registers[address : address + count]
        log.info("Read holding registers: %s", response.registers)
        return response

    def read_discrete_inputs(self, address=0, count=1) -> ModbusPDU:
        """Read discrete inputs."""
        log.info("Reading discrete inputs from %d to %d", address, address + count)
        response = MockModbusPDU()
        response.bits = self._discrete_inputs[address : address + count]
        return response

    def read_coils(self, address=0, count=1) -> ModbusPDU:
        """Read coils."""
        log.info("Reading coils from %d to %d", address, address + count)
        if address >= 0x200:
            address -= 0x200
        response = MockModbusPDU()
        response.bits = self._coils[address : address + count]
        log.info("Read coils: %s", response.bits)
        return response

    def write_coils(self, address, values) -> None:
        """Write coils."""
        log.info("Writing coils to %d with values %s", address, values)
        for i, value in enumerate(values):
            self._coils[address + i] = value

    def write_registers(self, address, values) -> None:
        """Write registers."""
        log.info("Writing registers to %d with values %s", address, values)
        for i, value in enumerate(values):
            self._holding_registers[address + i] = value

    def write_coil(self, address, value) -> None:
        """Write a coil."""
        log.info("Writing coil to %d with value %s", address, value)
        self.write_coils(address, [value])

    def write_register(self, address, value) -> None:
        """Write a register."""
        log.info("Writing register to %d with value %s", address, value)
        self.write_registers(address, [value])
