"""Common fixtures for pytest tests."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import json
import logging
from typing import Dict, Generator
from unittest.mock import patch

import pytest

from wg750xxx.settings import ModbusSettings
from wg750xxx.hub import Hub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient
from .mock.mock_modbus_tcp_client_for_dali_module import MockModbusTcpClientForDaliModule

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def modules() -> Dict[int, int]:
    """Define the default modules configuration.

    Returns:
        Dict mapping module_id to count
    """
    return {
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


@pytest.fixture(scope="module")
def modbus_mock() -> Generator[MockModbusTcpClient, None, None]:
    """Set up the standard modbus mock client for general testing.

    Returns:
        A mock ModbusTcpClient that simulates modbus responses
    """
    with patch("wg750xxx.hub.ModbusTcpClient") as modbus_tcp_client:
        yield MockModbusTcpClient(modbus_tcp_client)


@pytest.fixture(scope="module")
def modbus_mock_with_modules(modules: Dict[int, int]) -> Generator[MockModbusTcpClient, None, None]:
    """Set up the modbus mock client with specific modules configuration.

    Args:
        modules: Dictionary of module IDs to count

    Returns:
        A mock ModbusTcpClient configured with the specified modules
    """
    with patch("wg750xxx.hub.ModbusTcpClient") as modbus_tcp_client:
        yield MockModbusTcpClient(modbus_tcp_client, modules)


@pytest.fixture(scope="module")
def dali_modbus_mock() -> Generator[MockModbusTcpClientForDaliModule, None, None]:
    """Create a mock for the ModbusTcpClient specifically for DALI modules.

    Returns:
        A specialized mock for DALI module testing
    """
    with patch("wg750xxx.hub.ModbusTcpClient") as modbus_tcp_client:
        mock: MockModbusTcpClientForDaliModule = MockModbusTcpClientForDaliModule(modbus_tcp_client)
        yield mock


@pytest.fixture(scope="module")
def basic_hub(modbus_mock: MockModbusTcpClient) -> Generator[Hub, None, None]:
    """Set up a basic hub with no modules.

    Args:
        modbus_mock: The configured mock ModbusTcpClient

    Returns:
        A Hub instance with no modules
    """
    modbus_settings = ModbusSettings(server="dummy", port=502)
    hub_instance = Hub(modbus_settings, initialize=False)
    hub_instance.connect()
    hub_instance.initialize(discovery=False)
    yield hub_instance


@pytest.fixture(scope="module")
def configured_hub(modbus_mock_with_modules: MockModbusTcpClient) -> Generator[Hub, None, None]:
    """Set up a hub with specific module configuration.

    Args:
        modbus_mock_with_modules: The configured mock ModbusTcpClient

    Returns:
        A Hub instance with the specified modules
    """
    modbus_settings = ModbusSettings(server="dummy", port=502)
    # Initialize the hub with the modbus settings but don't automatically initialize
    hub_instance = Hub(modbus_settings, initialize=False)
    # Manually connect the hub (this will set up the client)
    hub_instance.connect()
    # Now run the full initialization
    hub_instance.initialize(discovery=True)

    logger.info(
        json.dumps(
            [i.config_dump() for i in hub_instance.modules],
            sort_keys=True,
            indent=4,
            default=str,
        )
    )
    yield hub_instance


@pytest.fixture(scope="module")
def dali_hub(dali_modbus_mock: MockModbusTcpClientForDaliModule) -> Generator[Hub, None, None]:
    """Create a hub with the DALI-specific ModbusTcpClient mock.

    Args:
        dali_modbus_mock: The mock for the ModbusTcpClient specialized for DALI

    Returns:
        A Hub instance configured for DALI module testing
    """
    modbus_settings = ModbusSettings(server="dummy", port=502)
    # Initialize the hub with the modbus settings but don't automatically initialize
    hub_instance = Hub(modbus_settings, initialize=False)
    # Manually connect the hub (this will set up the client)
    hub_instance.connect()
    # Now run the full initialization
    hub_instance.initialize(discovery=True)

    logger.info(
        json.dumps(
            [i.config_dump() for i in hub_instance.modules],
            sort_keys=True,
            indent=4,
            default=str,
        )
    )
    yield hub_instance
