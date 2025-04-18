"""Test the Dali module."""

# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,line-too-long
import json
import logging
from typing import cast, List, Generator
from unittest.mock import patch

import pytest

from wg750xxx.settings import ModbusSettings
from wg750xxx.hub import Hub
from wg750xxx.modules.dali.dali_commands import DaliCommands
from wg750xxx.modules.dali.dali_communication import DaliOutputMessage
from wg750xxx.modules.dali.modules import Wg750DaliMaster

from .mock.mock_modbus_tcp_client_for_dali_module import (
    MockModbusTcpClientForDaliModule,
)

# @unittest.skip("reason for skipping")

log: logging.Logger = logging.getLogger(__name__)


# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def modbus_tcp_client_mock() -> Generator[MockModbusTcpClientForDaliModule, None, None]:
    """Create a mock for the ModbusTcpClient."""
    with patch("wg750xxx.hub.ModbusTcpClient") as modbus_tcp_client:
        mock: MockModbusTcpClientForDaliModule = MockModbusTcpClientForDaliModule(modbus_tcp_client)
        yield mock


# pylint: disable=redefined-outer-name,unused-argument
@pytest.fixture(scope="module")
def hub(modbus_tcp_client_mock: MockModbusTcpClientForDaliModule) -> Generator[Hub, None, None]:
    """Create a hub with the mock ModbusTcpClient.

    Args:
        modbus_tcp_client_mock: The mock for the ModbusTcpClient,
                                automatically installed by the fixture.
                                While it appears unused in this function,
                                the patch in modbus_tcp_client_mock is
                                active during this fixture's execution,
                                allowing the Hub to use the mock internally.

    Returns:
        A configured Hub instance
    """
    # The mock is used implicitly when the Hub creates its connection
    # as the patch from modbus_tcp_client_mock fixture is still active
    modbus_settings: ModbusSettings = ModbusSettings(server="dummy", port=502)
    hub_instance: Hub = Hub(modbus_settings, [])
    log.info(
        json.dumps(
            [i.config_dump() for i in hub_instance.modules],
            sort_keys=True,
            indent=4,
            default=str,
        )
    )
    yield hub_instance


def test_dali_module_present(hub: Hub) -> None:
    """Test if the Dali module is present."""
    assert 641 in [module.module_identifier for module in hub.modules]


def test_dali_module_io_type(hub: Hub) -> None:
    """Test the IO type of the Dali module."""
    assert not hub.modules["641"][0].spec.io_type.digital, (
        "Dali should not be digital"
    )
    assert hub.modules["641"][0].spec.io_type.input, (
        "Dali module should be input"
    )
    assert hub.modules["641"][0].spec.io_type.output, (
        "Dali module should be output"
    )


def test_dali_module_modbus_channel_spec(hub: Hub) -> None:
    """Test the modbus channel specification of the Dali module."""
    assert "discrete" not in hub.modules["641"][0].spec.modbus_channels, (
        "Dali module should not have any discrete channels"
    )
    assert "coil" not in hub.modules["641"][0].spec.modbus_channels, (
        "Dali module should have have any coil channels"
    )
    assert hub.modules["641"][0].spec.modbus_channels["input"] == 3, (
        "Dali module should have 3 input channels"
    )
    assert hub.modules["641"][0].spec.modbus_channels["holding"] == 3, (
        "Dali module should have 3 holding channels"
    )


def test_dali_module_modbus_channels(hub: Hub) -> None:
    """Test the modbus channels of the Dali module."""
    assert len(hub.modules["641"][0].modbus_channels["input"]) == 3, (
        "Dali module should have 3 input channels"
    )
    assert len(hub.modules["641"][0].modbus_channels["holding"]) == 3, (
        "Dali module should have 3 holding channels"
    )


def test_transmit_request_control_bit(
    hub: Hub, modbus_tcp_client_mock: MockModbusTcpClientForDaliModule
) -> None:
    """Test the transmit request control bit."""
    modbus_tcp_client_mock.initialize_state()
    hub.connection.update_state()
    assert (
        hub.modules["641"][0].modbus_channels["holding"][0].read_lsb() == 0
    ), "Dali module should have 0 as control byte"
    assert hub.modules["641"][0].modbus_channels["input"][0].read_lsb() == 0, (
        "Dali module should have 0 as status byte"
    )
    cast(
        Wg750DaliMaster, hub.modules["641"][0]
    ).dali_communication_register.control_byte.transmit_request = True
    cast(
        Wg750DaliMaster, hub.modules["641"][0]
    ).dali_communication_register.write(DaliOutputMessage(command_code=0))
    hub.connection.update_state()
    log.info(
        "Status byte in modbus state: %s",
        f"{hub.modules['641'][0].modbus_channels['input'][0].read_lsb():08b}",
    )
    assert hub.modules["641"][0].modbus_channels["input"][0].read_lsb() == 1, (
        "Dali module should have 1 as status byte after setting transmit request control bit"
    )


def test_dali_command_query_short_address_present(
    hub: Hub, modbus_tcp_client_mock: MockModbusTcpClientForDaliModule
) -> None:
    """Test the query short address present command."""
    modbus_tcp_client_mock.initialize_state()
    hub.connection.update_state()
    command: DaliCommands = DaliCommands(
        cast(
            Wg750DaliMaster, hub.modules["641"][0]
        ).dali_communication_register
    )
    result: List[int] = command.query_short_address_present()
    log.info("Result of query short address present: %s", result)
    assert result == [
        2,
        7,
        10,
        14,
        18,
        21,
        26,
        28,
        32,
        36,
        40,
        45,
        48,
        54,
        56,
        63,
    ], (
        f"Dali module should return the correct short addresses present (expected [2, 7, 10, 14, 18, 21, 26, 28, 32, 36, 40, 45, 48, 54, 56, 63]), but got {result}"
    )
