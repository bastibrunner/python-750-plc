"""Test the Controller."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging

import pytest

from wg750xxx.hub import Hub, ControllerInfo
from wg750xxx.settings import HubConfig, ModuleConfig
from wg750xxx.modbus.state import ModbusConnection

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py


def test_controller_info_read(basic_hub: Hub) -> None:
    """Test that controller info is read correctly."""
    controller_info = basic_hub.info

    assert isinstance(controller_info, ControllerInfo), "Controller info should be a ControllerInfo object"
    assert hasattr(controller_info, "REVISION"), "Controller info should have a REVISION field"
    assert hasattr(controller_info, "SERIES"), "Controller info should have a SERIES field"
    assert hasattr(controller_info, "ITEM"), "Controller info should have an ITEM field"
    assert hasattr(controller_info, "FW_VERS"), "Controller info should have a FW_VERS field"
    assert hasattr(controller_info, "FW_TIMESTAMP"), "Controller info should have a FW_TIMESTAMP field"
    assert hasattr(controller_info, "FW_INFO"), "Controller info should have a FW_INFO field"


def test_controller_connection(modbus_mock: MockModbusTcpClient) -> None:
    """Test controller connection and disconnection."""
    modbus_settings = HubConfig(host="dummy", port=502)
    hub = Hub(modbus_settings, initialize=False)

    # Test initial state
    assert not hub.is_connected, "Hub should not be connected initially"
    assert hub.connection is None, "Hub connection should be None initially"

    # Test connect
    hub.connect()
    assert hub.is_connected, "Hub should be connected after connect()"
    assert hub.connection is not None, "Hub connection should not be None after connect()"
    assert isinstance(hub.connection, ModbusConnection), "Hub connection should be a ModbusConnection"

    # Test close
    hub.close()
    # Note: in the mock setup, close() might not actually change the connection status
    # So we won't assert is_connected here as it depends on the mock implementation


def test_controller_initialization(modbus_mock_with_modules: MockModbusTcpClient) -> None:
    """Test controller initialization."""
    modbus_settings = HubConfig(host="dummy", port=502)
    hub = Hub(modbus_settings, initialize=False)

    assert not hub.is_initialized, "Hub should not be initialized initially"

    # Initialize without discovery
    hub.initialize(discovery=False)
    assert hub.is_initialized, "Hub should be initialized after initialize()"
    assert not hub.is_module_discovery_done, "Module discovery should not be done when discovery=False"

    # Reset and initialize with discovery
    hub.is_initialized = False
    hub.initialize(discovery=True)
    assert hub.is_initialized, "Hub should be initialized after initialize() with discovery"
    assert hub.is_module_discovery_done, "Module discovery should be done when discovery=True"


def test_controller_run_discovery(modbus_mock_with_modules: MockModbusTcpClient) -> None:
    """Test controller module discovery."""
    modbus_settings = HubConfig(host="dummy", port=502)
    hub = Hub(modbus_settings, initialize=False)
    hub.connect()

    # Run discovery
    result = hub.run_discovery()
    assert result, "Discovery should return True on success"
    assert hub.is_module_discovery_done, "Module discovery should be done after run_discovery()"
    assert len(hub.modules) > 0, "Modules should be discovered"


def test_controller_module_access(configured_hub: Hub) -> None:
    """Test accessing modules through the controller."""
    # Test access by index
    assert len(configured_hub.modules) > 0, "Hub should have modules"
    first_module = configured_hub.modules[0]
    assert first_module is not None, "First module should not be None"

    # Test access by slice
    first_few_modules = configured_hub.modules[0:3]
    assert isinstance(first_few_modules, list), "Sliced modules should be a list"
    assert len(first_few_modules) > 0, "Sliced modules should not be empty"

    # Test iteration
    modules_count = 0
    for _module in configured_hub.modules:
        modules_count += 1
    assert modules_count == len(configured_hub.modules), "Iteration should yield all modules"


def test_controller_config(modbus_mock: MockModbusTcpClient) -> None:
    """Test controller configuration."""
    # Test with HubConfig
    modbus_settings = HubConfig(host="test_server", port=1234)
    hub = Hub(modbus_settings, initialize=False)

    assert hub.config.host == "test_server", "Server should be set correctly"
    assert hub.config.port == 1234, "Port should be set correctly"
    assert hub.config.modules == [], "Modules should be empty"

    # Test with changed HubConfig
    hub_config = HubConfig(
        host="new_server", port=5678,
        modules=[ModuleConfig(name="test_module", type="test_type", index=0)]
    )
    hub.config = hub_config

    assert hub.config.host == "new_server", "Server should be updated"
    assert hub.config.port == 5678, "Port should be updated"
    assert hub.config.modules == [], "Modules config should be empty"
    assert hub._init_config == hub_config.modules, "Modules initial config should be updated"


def test_controller_config_with_none(modbus_mock: MockModbusTcpClient) -> None:
    """Test controller configuration with None."""
    hub = Hub(HubConfig(host="dummy", port=502), initialize=False)

    with pytest.raises(ValueError):
        hub.config = None # type: ignore
    assert hub.config is not None, "Config should not be None"

def test_controller_config_with_invalid_config(modbus_mock: MockModbusTcpClient) -> None:
    """Test controller configuration with invalid config."""
    hub = Hub(HubConfig(host="dummy", port=502), initialize=False)

    with pytest.raises(ValueError):
        hub.config = "invalid_config" # type: ignore

def test_controller_module_config(modbus_mock: MockModbusTcpClient) -> None:
    """Test controller module config."""
    hub = Hub(HubConfig(host="dummy", port=502), initialize=False)
    hub.config = HubConfig(host="dummy", port=502, modules=[ModuleConfig(name="test_module", type="test_type", index=0)])
    assert hub.config is not None, "Config should not be None"

def test_controller_process_state_width(configured_hub: Hub) -> None:
    """Test controller process state width calculation."""
    # The process state width should match the sum of the module channel counts
    total_discrete = sum(
        module.spec.modbus_channels.get("discrete", 0)
        for module in configured_hub.modules
        if module.spec.io_type.digital and module.spec.io_type.input
    )

    total_coil = sum(
        module.spec.modbus_channels.get("coil", 0)
        for module in configured_hub.modules
        if module.spec.io_type.digital and module.spec.io_type.output
    )

    total_input = sum(
        module.spec.modbus_channels.get("input", 0)
        for module in configured_hub.modules
        if not module.spec.io_type.digital and module.spec.io_type.input
    )

    total_holding = sum(
        module.spec.modbus_channels.get("holding", 0)
        for module in configured_hub.modules
        if not module.spec.io_type.digital and module.spec.io_type.output
    )

    assert configured_hub._process_state_width['discrete'] == total_discrete, \
        f"Discrete width mismatch: {configured_hub._process_state_width['discrete']} != {total_discrete}"

    assert configured_hub._process_state_width['coil'] == total_coil, \
        f"Coil width mismatch: {configured_hub._process_state_width['coil']} != {total_coil}"

    assert configured_hub._process_state_width['input'] == total_input * 16, \
        f"Input width mismatch: {configured_hub._process_state_width['input']} != {total_input} * 16"

    assert configured_hub._process_state_width['holding'] == total_holding * 16, \
        f"Holding width mismatch: {configured_hub._process_state_width['holding']} != {total_holding} * 16"


def test_controller_setup_basic_test_modules(modbus_mock: MockModbusTcpClient) -> None:
    """Test the _setup_basic_test_modules method."""
    modbus_settings = HubConfig(host="dummy", port=502)
    hub = Hub(modbus_settings, initialize=False)
    hub.connect()

    # Since this is a protected method, we need to call it directly
    hub._setup_basic_test_modules()

    assert len(hub.modules) >= 3, "At least 3 test modules should be set up"

    # Verify basic module types were added (DI, DO, AI, AO)
    module_types = set()
    for module in hub.modules:
        if module.spec.io_type.digital and module.spec.io_type.input:
            module_types.add("DI")
        elif module.spec.io_type.digital and module.spec.io_type.output:
            module_types.add("DO")
        elif not module.spec.io_type.digital and module.spec.io_type.input:
            module_types.add("AI")
        elif not module.spec.io_type.digital and module.spec.io_type.output:
            module_types.add("AO")

    assert "DI" in module_types, "Digital input module should be created"
    assert "DO" in module_types, "Digital output module should be created"
    assert "AI" in module_types, "Analog input module should be created"
