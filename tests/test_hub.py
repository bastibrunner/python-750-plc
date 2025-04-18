"""Test the Hub."""

# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,line-too-long,protected-access
import json
import logging
from unittest.mock import patch, MagicMock
from typing import Dict

import pytest

from wg750xxx.settings import ModbusSettings
from wg750xxx.hub import Hub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def modules() -> Dict[int, int]:
    """Define the modules configuration."""
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
@patch("wg750xxx.hub.ModbusTcpClient")
# pylint: disable=redefined-outer-name
def hub_fixture(modbus_tcp_client: MagicMock, modules: Dict[int, int]) -> Hub:
    """Set up the hub fixture."""
    MockModbusTcpClient(modbus_tcp_client, modules)
    modbus_settings = ModbusSettings(server="dummy", port=502)
    hub = Hub(modbus_settings, [])
    logger.info(
        json.dumps(
            [i.config_dump() for i in hub.modules],
            sort_keys=True,
            indent=4,
            default=str,
        )
    )
    return hub


# pylint: disable=redefined-outer-name
def test_module_digital_input_bits_match(hub_fixture: Hub) -> None:
    """Test if the digital input configuration matches the configured modules."""
    sum_bits_configured_modules: int = sum(
        i.spec.modbus_channels.get("discrete", 0)
        for i in hub_fixture.modules
        if i.spec.io_type.digital and i.spec.io_type.input
    )
    assert hub_fixture._process_state_width["discrete"] == sum_bits_configured_modules, (
        f"Error: Digital input configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({hub_fixture._process_state_width['discrete']})"
    )


# pylint: disable=redefined-outer-name
def test_module_digital_output_bits_match(hub_fixture: Hub) -> None:
    """Test if the digital output configuration matches the configured modules."""
    sum_bits_configured_modules: int = sum(
        i.spec.modbus_channels.get("coil", 0)
        for i in hub_fixture.modules
        if i.spec.io_type.digital and i.spec.io_type.output
    )
    assert hub_fixture._process_state_width["coil"] == sum_bits_configured_modules, (
        f"Error: Digital output configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({hub_fixture._process_state_width['coil']})"
    )


# pylint: disable=redefined-outer-name
def test_module_analog_input_bits_match(hub_fixture: Hub) -> None:
    """Test if the analog input configuration matches the configured modules."""
    sum_bits_configured_modules: int = (
        sum(
            i.spec.modbus_channels.get("input", 0)
            for i in hub_fixture.modules
            if not i.spec.io_type.digital and i.spec.io_type.input
        )
        * 16
    )
    assert hub_fixture._process_state_width["input"] == sum_bits_configured_modules, (
        f"Error: Analog input configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({hub_fixture._process_state_width['input']})"
    )


# pylint: disable=redefined-outer-name
def test_module_analog_output_bits_match(hub_fixture: Hub) -> None:
    """Test if the analog output configuration matches the configured modules."""
    sum_bits_configured_modules: int = (
        sum(
            i.spec.modbus_channels.get("holding", 0)
            for i in hub_fixture.modules
            if not i.spec.io_type.digital and i.spec.io_type.output
        )
        * 16
    )
    assert hub_fixture._process_state_width["holding"] == sum_bits_configured_modules, (
        f"Error: Analog output configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({hub_fixture._process_state_width['holding']})"
    )


# pylint: disable=redefined-outer-name
def test_channel_count_match_all_modules(hub_fixture: Hub) -> None:
    """Test if the channel count matches the configured modules."""
    for module in hub_fixture.modules:
        channels_spec: int = sum(module.spec.modbus_channels.values())
        channels: int = sum(len(i) for i in module.modbus_channels.values())
        assert channels_spec == channels, (
            f"Error in Module {module.display_name}: Channel count mismatch: spec ({channels_spec}) != channels ({channels})"
        )


# pylint: disable=redefined-outer-name
def test_all_configured_modules_present(hub_fixture: Hub, modules: Dict[int, int]) -> None:
    """Test if all configured modules are present."""
    for module_id in modules:
        assert module_id in [
            module.module_identifier for module in hub_fixture.modules
        ], f"Module {module_id} is missing from the hub"
