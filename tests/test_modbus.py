"""Test the Modbus channel."""

# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring,line-too-long
# pylint: disable=redefined-outer-name,import-error,unused-argument

import json
import logging
from random import randint
from typing import Generator
from unittest.mock import patch

import pytest

from wg750xxx.settings import ModbusSettings
from wg750xxx.hub import Hub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient



logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def modbus_mock() -> Generator[MockModbusTcpClient, None, None]:
    """Set up the modbus mock client."""
    with patch("wg750xxx.hub.ModbusTcpClient") as modbus_tcp_client:
        yield MockModbusTcpClient(modbus_tcp_client)


@pytest.fixture(scope="module")
def hub(modbus_mock: MockModbusTcpClient) -> Hub:
    """Set up the hub."""
    modbus_settings = ModbusSettings(server="dummy", port=502)
    hub_instance = Hub(modbus_settings, True)
    logger.info(
        json.dumps(
            [i.config_dump() for i in hub_instance.modules],
            sort_keys=True,
            indent=4,
            default=str,
        )
    )
    return hub_instance


def test_modbus_discrete_input_channel_read(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read method of the Discrete input channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has digital input
            if not module.spec.io_type.digital or not module.spec.io_type.input:
                continue
            for channel in module.modbus_channels["discrete"]:
                channel_value = channel.read()
                mock_value = bool(
                    modbus_mock.read_discrete_inputs(
                        channel.address
                    ).bits[0]
                )
                assert channel_value == mock_value, (
                    f"Error: Discrete input channel #{channel.address} read mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value})"
                )
                address += 1
        assert address > 0, "Error: No Discrete input channels found"


def test_modbus_coil_channel_read(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read method of the Coil channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has digital output
            if not module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["coil"]:
                channel_value = channel.read()
                mock_value = modbus_mock.read_coils(
                    channel.address
                ).bits[0]
                assert channel_value == mock_value, (
                    f"Error: Coil channel #{channel.address} read mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value})"
                )
                address += 1
        assert address > 0, "Error: No Coil channels found"


def test_modbus_input_channel_read(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read method of the Input channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog input
            if module.spec.io_type.digital or not module.spec.io_type.input:
                continue
            for channel in module.modbus_channels["input"]:
                channel_value = channel.read()
                mock_value = modbus_mock.read_input_registers(
                    channel.address
                ).registers[0]
                assert channel_value == mock_value, (
                    f"Error: Input channel #{channel.address} read mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Input channels found"


def test_modbus_holding_channel_read(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read method of the Holding channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog output
            if module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["holding"]:
                channel_value = channel.read()
                mock_value = modbus_mock.read_holding_registers(
                    channel.address
                ).registers[0]
                assert channel_value == mock_value, (
                    f"Error: Holding channel #{channel.address} read mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Holding channels found"


def test_modbus_coil_channel_write(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the write method of the Coil channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has digital output
            if not module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["coil"]:
                value = bool(randint(0, 1))
                channel.write(value)
                mock_value = modbus_mock.read_coils(
                    channel.address
                ).bits[0]
                assert value == mock_value, (
                    f"Error: Coil channel #{channel.address} write mismatch: Channel Value ({value}) != Mock Value ({mock_value})"
                )
                address += 1
        assert address > 0, "Error: No Coil channels found"


def test_modbus_holding_channel_write(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the write method of the Holding channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog output
            if module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["holding"]:
                value = randint(0, 65535)
                channel.write(value)
                mock_value = modbus_mock.read_holding_registers(
                    channel.address
                ).registers[0]
                assert value == mock_value, (
                    f"Error: Holding channel #{channel.address} write mismatch: Channel Value ({value:02x}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Holding channels found"


def test_modbus_input_channel_read_lsb(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read_lsb method of the Input channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog input
            if module.spec.io_type.digital or not module.spec.io_type.input:
                continue
            for channel in module.modbus_channels["input"]:
                channel_value = channel.read_lsb()
                mock_value = (
                    modbus_mock.read_input_registers(
                        address
                    ).registers[0]
                    & 0xFF
                )
                assert channel_value == mock_value, (
                    f"Error: Input channel #{channel.address} read lsb mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Input channels found"


def test_modbus_input_channel_read_msb(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the read_msb method of the Input channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog input
            if module.spec.io_type.digital or not module.spec.io_type.input:
                continue
            for channel in module.modbus_channels["input"]:
                channel_value = channel.read_msb()
                mock_value = (
                    modbus_mock.read_input_registers(
                        address
                    ).registers[0]
                    & 0xFF00
                ) >> 8
                assert channel_value == mock_value, (
                    f"Error: Input channel #{channel.address} read msb mismatch: Channel Value ({channel_value}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Input channels found"


def test_modbus_holding_channel_write_lsb(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the write_lsb method of the Holding channel."""
    for _ in range(50):
        # modbus_mock.randomize_state()
        # hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog output
            if module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["holding"]:
                value = randint(0, 255)
                channel.write_lsb(value)
                mock_value = (
                    modbus_mock.read_holding_registers(
                        channel.address
                    ).registers[0]
                    & 0xFF
                )
                assert value == mock_value, (
                    f"Error: Holding channel #{channel.address} write lsb mismatch: Channel Value ({value:02x}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Holding channels found"


def test_modbus_holding_channel_write_msb(modbus_mock: MockModbusTcpClient, hub: Hub) -> None:
    """Test the write_msb method of the Holding channel."""
    for _ in range(50):
        modbus_mock.randomize_state()
        hub.connection.update_state()
        address = 0
        for module in hub.modules:
            # Check if module has analog output
            if module.spec.io_type.digital or not module.spec.io_type.output:
                continue
            for channel in module.modbus_channels["holding"]:
                value = randint(0, 255)
                channel.write_msb(value)
                mock_value = (
                    modbus_mock.read_holding_registers(
                        channel.address
                    ).registers[0]
                    & 0xFF00
                ) >> 8
                assert value == mock_value, (
                    f"Error: Holding channel #{channel.address} write msb mismatch: Channel Value ({value:02x}) != Mock Value ({mock_value:02x})"
                )
                address += 1
        assert address > 0, "Error: No Holding channels found"
