"""Test the Dali module."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

import logging
from typing import cast

import pytest

from wg750xxx.modules.dali.dali_communication import DaliOutputMessage
from wg750xxx.modules.dali.module_setup import ModuleSetup
from wg750xxx.modules.dali.modules import DaliChannel, Wg750DaliMaster
from wg750xxx.wg750xxx import PLCHub

from .mock.mock_modbus_tcp_client_for_dali_module import (
    MockModbusTcpClientForDaliModule,
)

log: logging.Logger = logging.getLogger(__name__)

# Using fixtures from conftest.py now


# A fixture for this module that holds a wago module instance
@pytest.fixture
def dali_module(dali_hub: PLCHub) -> Wg750DaliMaster:
    """Fixture for this module that holds a wago module instance."""
    dali_module_instance = dali_hub.modules["641"]
    assert dali_module_instance is not None, "Dali module should be present"
    assert isinstance(dali_module_instance, Wg750DaliMaster), (
        "Dali module should be a Wg750DaliMaster"
    )
    assert dali_module_instance.channels is not None, "Dali module should have channels"
    return dali_module_instance


def test_dali_module_present(dali_hub: PLCHub) -> None:
    """Test if the Dali module is present."""
    assert 641 in [module.module_identifier for module in dali_hub.modules]


def test_dali_module_io_type(dali_module: Wg750DaliMaster) -> None:
    """Test the IO type of the Dali module."""
    assert not dali_module.spec.io_type.digital, "Dali should not be digital"
    assert dali_module.spec.io_type.input, "Dali module should be input"
    assert dali_module.spec.io_type.output, "Dali module should be output"


def test_dali_module_modbus_channel_spec(dali_module: Wg750DaliMaster) -> None:
    """Test the modbus channel specification of the Dali module."""
    assert "discrete" not in dali_module.spec.modbus_channels, (
        "Dali module should not have any discrete channels"
    )
    assert "coil" not in dali_module.spec.modbus_channels, (
        "Dali module should have have any coil channels"
    )
    assert dali_module.spec.modbus_channels["input"] == 3, (
        "Dali module should have 3 input channels"
    )
    assert dali_module.spec.modbus_channels["holding"] == 3, (
        "Dali module should have 3 holding channels"
    )


def test_dali_module_modbus_channels(dali_module: Wg750DaliMaster) -> None:
    """Test the modbus channels of the Dali module."""
    assert len(dali_module.modbus_channels["input"]) == 3, (
        "Dali module should have 3 input channels"
    )
    assert len(dali_module.modbus_channels["holding"]) == 3, (
        "Dali module should have 3 holding channels"
    )


def test_transmit_request_control_bit(
    dali_hub: PLCHub,
    dali_modbus_mock: MockModbusTcpClientForDaliModule,
    dali_module: Wg750DaliMaster,
) -> None:
    """Test the transmit request control bit."""
    dali_modbus_mock.initialize_state()
    assert dali_hub.connection is not None, "Dali hub should be connected"
    dali_hub.connection.update_state()
    assert dali_module.modbus_channels["holding"][0].read_lsb() == 0, (
        "Dali module should have 0 as control byte"
    )
    assert dali_module.modbus_channels["input"][0].read_lsb() == 0, (
        "Dali module should have 0 as status byte"
    )
    cast(
        Wg750DaliMaster, dali_hub.modules["641"]
    ).dali_communication_register.control_byte.transmit_request = True
    cast(Wg750DaliMaster, dali_hub.modules["641"]).dali_communication_register.write(
        DaliOutputMessage(command_code=0)
    )
    dali_hub.connection.update_state()
    log.info(
        "Status byte in modbus state: %s",
        f"{dali_module.modbus_channels['input'][0].read_lsb():08b}",
    )
    assert dali_module.modbus_channels["input"][0].read_lsb() == 1, (
        "Dali module should have 1 as status byte after setting transmit request control bit"
    )


def test_dali_module_returns_correct_type_when_indexed(
    dali_hub: PLCHub,
    dali_modbus_mock: MockModbusTcpClientForDaliModule,
    dali_module: Wg750DaliMaster,
) -> None:
    """Test the Dali module returns the correct type when indexed."""
    assert isinstance(dali_module[0], DaliChannel), (
        "Fetching element from DaliHub should return a DaliChannel"
    )
    module_slice = dali_module[0:5]
    assert isinstance(module_slice, list), "Sliced DaliHub should be a List"
    assert all(isinstance(channel, DaliChannel) for channel in module_slice), (
        "All items in sliced DaliHub should be DaliChannel instances"
    )


def test_dali_command_query_short_address_present(
    dali_hub: PLCHub,
    dali_modbus_mock: MockModbusTcpClientForDaliModule,
    dali_module: Wg750DaliMaster,
) -> None:
    """Test the query short address present command."""
    dali_modbus_mock.initialize_state()
    assert dali_hub.connection is not None, "Dali hub should be connected"
    dali_hub.connection.update_state()
    command: ModuleSetup = ModuleSetup(dali_module.dali_communication_register)
    result: list[int] = command.query_short_address_present()
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
    ], f"""Dali module should return the correct short addresses present.
        expected [2, 7, 10, 14, 18, 21, 26, 28, 32, 36, 40, 45, 48, 54, 56, 63],
        actual   {result}"""
