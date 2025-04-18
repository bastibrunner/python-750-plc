"""A Wago 750 Hub.

Represents a Wago 750 controller and its connected modules.
"""

from collections.abc import Iterator
import logging
from typing import cast

from pydantic import BaseModel
from pymodbus.client import ModbusTcpClient

from .modules.identifier import ModuleIdentifier
from .modbus.state import AddressDict, ModbusChannelSpec, ModbusConnection
from .modules.module import WagoModule
from .modules.spec import IOType
from .modbus.registers import Register, test_constants
from .settings import HubConfig

log = logging.getLogger(__name__)


class ControllerInfo(BaseModel):
    """Controller info."""

    REVISION: int
    SERIES: int
    ITEM: int
    FW_VERS: str
    FW_TIMESTAMP: str
    FW_INFO: str


class Modules:
    """Modules."""

    def __init__(self) -> None:
        """Initialize the modules."""
        self._modules: list[WagoModule] = []

    def append_module(self, module: WagoModule) -> None:
        """Append a module to the modules."""
        self._modules.append(module)

    def reset_modules(self) -> None:
        """Reset the modules."""
        self._modules = []

    def all(self) -> list[WagoModule]:
        """Get the modules."""
        return self._modules

    def get(self, io_type: IOType | None = None, module: str | None = None) -> list[WagoModule]:
        """Get the modules."""
        if io_type:
            return [i for i in self._modules if i.spec.io_type == io_type]
        if module:
            return [i for i in self._modules if i.spec.module_type == module or module in i.aliases]
        return self._modules

    def __len__(self) -> int:
        """Get the number of modules."""
        return len(self._modules)

    def __getitem__(self, index: slice | int) -> list[WagoModule] | WagoModule:
        """Get the modules at a specific index or slice."""
        return self._modules[index]

    def __iter__(self) -> Iterator[WagoModule]:
        """Iterate over the modules."""
        return iter(self._modules)

    def __str__(self) -> str:
        """Get the string representation of the modules."""
        return str(self._modules)


class Hub:
    """The main class for the Wago 750 Modbus TCP server.

    Args:
        host (str): The hostname or IP address of the Wago Modbus TCP server.
        port (int): The port of the Wago Modbus TCP server.
        discovery (bool): Whether to run the discovery process.

    Properties:
        info (dict): A dictionary containing information about the controller.
        connected_modules (list[WagoModule]): A list of connected modules in order of their address on the bus.
        modules (dict[str,list[WagoModule]]): A dictionary of connected modules grouped by type. Each type is a key in the dictionary
            and has a list of module instances in order of their address on the bus.
        next_address (AddressDict): The next address to be used for a new module.
        process_state_width (ModbusChannelSpec): The width of the process state.
        client (ModbusTcpClient): The Modbus TCP client.

    """

    _first_address: AddressDict = {"coil": 0, "discrete": 0, "input": 0, "holding": 0}

    def __init__(self, config: HubConfig, initialize: bool = True) -> None:
        """Initialize the hub."""
        self.config = config
        self.modules: Modules = Modules()
        self._discovered_modules: list[int] = []
        self._process_state_width: ModbusChannelSpec = ModbusChannelSpec(
            input=0, holding=0, discrete=0, coil=0
        )
        self._client: ModbusTcpClient | None = None
        self.connection: ModbusConnection | None = None
        self.is_initialized: bool = False
        self.is_module_discovery_done: bool = False
        self._next_address: AddressDict = self._first_address.copy()
        if initialize:
            self.initialize()

    def connect(self) -> None:
        """Connect to the hub."""
        self._client = ModbusTcpClient(
            self._modbus_host, port=self._modbus_port, timeout=5
        )
        self._client.connect()
        self._process_state_width = self._read_data_width_in_state()
        self.connection = ModbusConnection(
            modbus_tcp_client=self._client, bits_in_state=self._process_state_width
        )
        self.connection.update_state()

    @property
    def is_connected(self) -> bool:
        """Check if the hub is connected."""
        return self._client.connected

    def initialize(self, discovery: bool = True) -> None:
        """Initialize the hub."""
        if self.is_initialized:
            return
        self.reset_modules()
        if not self.is_connected:
            self.connect()

        self.info: ControllerInfo = self._read_controller_info()
        self.connection.update_state()
        if discovery:
            self.run_discovery()
        self.is_initialized = True
        log.debug(self.info)
        log.debug(self.modules)

    def run_discovery(self) -> None:
        """Run the discovery process."""
        self.is_module_discovery_done = False
        try:
            self._get_connected_modules_from_controller()
            self.is_module_discovery_done = True
        except NotImplementedError as e:
            log.error("Not implemented: %s", e)

    def _read_description(self) -> str:
        """Read the description."""
        response = self._read_register(0x2001, width=1)
        return str(response)

    # def _read_test_constants(self) -> dict[int,int]:
    #     return { address: self.client.read_input_registers(address,count=1)[0] for address in test_constants.keys() }

    def _read_register(self, address: int, width: int = 1) -> Register:
        """Read the register."""
        response = self._client.read_input_registers(address, count=width)
        return Register(address, response.registers)

    def _read_and_check_test_constants(self) -> None:
        """Read and check the test constants."""
        for item in test_constants:
            register = self._read_register(item.address)
            log.debug("register: %s", str(register))
            assert item == register, f"Error: {item} != {register}"

    def _get_connected_modules_from_controller(self, reset: bool = True) -> None:
        """Read the connected modules from the controller."""
        self.reset_modules()
        register_values: list[int] = []
        for i in range(3):
            response = self._client.read_input_registers(0x2030 + i, count=64).registers
            register_values = register_values + response
        for value in register_values:
            if value != 0 and (len(self.modules) < 1 or reset):
                index = len(self.modules)
                module_settings = (
                    self._init_config[index] if index < len(self._init_config) else None
                )
                self.modules.append(
                    WagoModule.module_factory(
                        index=index,
                        module_identifier=ModuleIdentifier(value),
                        modbus_address=AddressDict(self._next_address),
                        modbus_connection=self.connection,
                        config=module_settings,
                    )
                )

    def append_module(self, module: WagoModule) -> None:
        """Append a module to the hub."""
        self.modules.append(module)
        self._next_address.update(cast(AddressDict, module.get_next_address()))

    def reset_modules(self) -> None:
        """Reset the modules."""
        self._process_state_width: ModbusChannelSpec = ModbusChannelSpec(
            input=0, holding=0, discrete=0, coil=0
        )
        self.modules = []
        self._next_address = self._first_address.copy()

    def _read_data_width_in_state(self) -> ModbusChannelSpec:
        """Read the data width in state."""
        return ModbusChannelSpec(
            holding=self._read_register(0x1022).value_to_int(),
            input=self._read_register(0x1023).value_to_int(),
            coil=self._read_register(0x1024).value_to_int(),
            discrete=self._read_register(0x1025).value_to_int(),
        )

    def _read_module_diagnostic(self) -> None:
        """Read the module diagnostic."""
        log.debug("module diagnostic: %s", self._read_register(0x1050, 3))

    def _read_controller_info(self) -> ControllerInfo:
        """Read the controller info."""
        revision = self._read_register(0x2010).value_to_int()
        series = self._read_register(0x2011).value_to_int()
        item = self._read_register(0x2012).value_to_int()
        fw_vers = (
            f"{self._read_register(0x2013).value_to_int()}."
            f"{self._read_register(0x2014).value_to_int()}"
        )
        fw_timestamp = (
            f"{self._read_register(0x2022, 8).value_to_string()} "
            f"{self._read_register(0x2021, 8).value_to_string()}"
        )
        fw_info = self._read_register(0x2023, 32).value_to_string()

        return ControllerInfo(
            REVISION=revision,
            SERIES=series,
            ITEM=item,
            FW_VERS=fw_vers,
            FW_TIMESTAMP=fw_timestamp,
            FW_INFO=fw_info,
        )

    def close(self) -> None:
        """Close the connection to the controller."""
        self._client.close()

    def __str__(self) -> str:
        """Return a string representation of the hub."""
        return str(self.config)

    @property
    def config(self) -> HubConfig:
        """Return a dictionary representation of the hub."""
        return HubConfig(
            host=self._modbus_host,
            port=self._modbus_port,
            modules=[module.config for module in self.modules],
            modules_dict={module.config.id: module.config for module in self.modules},
        )

    @config.setter
    def config(self, config: HubConfig) -> None:
        """Set the config of the hub."""
        self._modbus_host = config.host
        self._modbus_port = config.port
        self._init_config = config.modules
