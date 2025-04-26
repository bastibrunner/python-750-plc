"""Test the Dali module."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

import logging
from typing import cast, List

from wg750xxx.wg750xxx import PLCHub
from wg750xxx.modules.dali.module_setup import ModuleSetup
from wg750xxx.modules.dali.dali_communication import DaliOutputMessage
from wg750xxx.modules.dali.modules import Wg750DaliMaster, DaliChannel

from .mock.mock_modbus_tcp_client_for_dali_module import (
    MockModbusTcpClientForDaliModule,
)

log: logging.Logger = logging.getLogger(__name__)

# Using fixtures from conftest.py now


def test_dali_module_present(dali_hub: PLCHub) -> None:
    """Test if the Dali module is present."""
    assert 641 in [module.module_identifier for module in dali_hub.modules]


def test_dali_module_io_type(dali_hub: PLCHub) -> None:
    """Test the IO type of the Dali module."""
    assert isinstance(dali_hub.modules["641"], Wg750DaliMaster), (
        "Dali module should be a Wg750DaliMaster"
    )
    assert not dali_hub.modules["641"].spec.io_type.digital, (
        "Dali should not be digital"
    )
    assert dali_hub.modules["641"].spec.io_type.input, (
        "Dali module should be input"
    )
    assert dali_hub.modules["641"].spec.io_type.output, (
        "Dali module should be output"
    )


def test_dali_module_modbus_channel_spec(dali_hub: PLCHub) -> None:
    """Test the modbus channel specification of the Dali module."""
    assert "discrete" not in dali_hub.modules["641"].spec.modbus_channels, (
        "Dali module should not have any discrete channels"
    )
    assert "coil" not in dali_hub.modules["641"].spec.modbus_channels, (
        "Dali module should have have any coil channels"
    )
    assert dali_hub.modules["641"].spec.modbus_channels["input"] == 3, (
        "Dali module should have 3 input channels"
    )
    assert dali_hub.modules["641"].spec.modbus_channels["holding"] == 3, (
        "Dali module should have 3 holding channels"
    )


def test_dali_module_modbus_channels(dali_hub: PLCHub) -> None:
    """Test the modbus channels of the Dali module."""
    assert len(dali_hub.modules["641"].modbus_channels["input"]) == 3, (
        "Dali module should have 3 input channels"
    )
    assert len(dali_hub.modules["641"].modbus_channels["holding"]) == 3, (
        "Dali module should have 3 holding channels"
    )


def test_transmit_request_control_bit(
    dali_hub: PLCHub, dali_modbus_mock: MockModbusTcpClientForDaliModule
) -> None:
    """Test the transmit request control bit."""
    dali_modbus_mock.initialize_state()
    dali_hub.connection.update_state()
    assert (
        dali_hub.modules["641"].modbus_channels["holding"][0].read_lsb() == 0
    ), "Dali module should have 0 as control byte"
    assert dali_hub.modules["641"].modbus_channels["input"][0].read_lsb() == 0, (
        "Dali module should have 0 as status byte"
    )
    cast(
        Wg750DaliMaster, dali_hub.modules["641"]
    ).dali_communication_register.control_byte.transmit_request = True
    cast(
        Wg750DaliMaster, dali_hub.modules["641"]
    ).dali_communication_register.write(DaliOutputMessage(command_code=0))
    dali_hub.connection.update_state()
    log.info(
        "Status byte in modbus state: %s",
        f"{dali_hub.modules['641'].modbus_channels['input'][0].read_lsb():08b}",
    )
    assert dali_hub.modules["641"].modbus_channels["input"][0].read_lsb() == 1, (
        "Dali module should have 1 as status byte after setting transmit request control bit"
    )

def test_dali_module_returns_correct_type_when_indexed(
    dali_hub: PLCHub, dali_modbus_mock: MockModbusTcpClientForDaliModule
) -> None:
    """Test the Dali module returns the correct type when indexed."""
    assert isinstance(dali_hub.modules["641"], Wg750DaliMaster), (
        "Dali module should be a Wg750DaliMaster"
    )
    assert isinstance(dali_hub.modules["641"][0], DaliChannel), (
        "Fetching element from DaliHub should return a DaliChannel"
    )
    assert isinstance(dali_hub.modules["641"][0:5], list), (
        "Sliced DaliHub should be a List"
    )
    assert all(isinstance(module, DaliChannel) for module in dali_hub.modules["641"][0:5]), (
        "All items in sliced DaliHub should be DaliChannel instances"
    )

def test_dali_command_query_short_address_present(
    dali_hub: PLCHub, dali_modbus_mock: MockModbusTcpClientForDaliModule
) -> None:
    """Test the query short address present command."""
    dali_modbus_mock.initialize_state()
    dali_hub.connection.update_state() # type: ignore
    command: ModuleSetup = ModuleSetup(
        cast(
            Wg750DaliMaster, dali_hub.modules["641"][0] # type: ignore
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
        f"""Dali module should return the correct short addresses present.
        expected [2, 7, 10, 14, 18, 21, 26, 28, 32, 36, 40, 45, 48, 54, 56, 63],
        actual   {result}"""
    )
