"""Tests for the Wago PLC module configuration."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

from typing import List, Generator

import pytest
from wg750xxx.hub import Hub
from wg750xxx.settings import HubConfig
from wg750xxx.modules.module import ModuleConfig


@pytest.fixture(scope="module")
def hub() -> Generator[Hub, None, None]:
    """Create a Hub instance for testing."""
    hub_instance = Hub(HubConfig(host="10.22.22.16", port=502), True)
    yield hub_instance


@pytest.fixture(scope="module")
def module_config(hub: Hub) -> List[ModuleConfig]:
    """Store module configuration for debugging."""
    return [i.config_dump() for i in hub.modules]


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_read_register(hub: Hub) -> None:
    """Test reading registers."""
    client = hub._client
    if client is None:
        pytest.skip("No physical PLC connection")

    register = client.read_input_registers(
        0x0000, count=36
    )  # hub.count_bits_digital_in / 16
    # Store register values for debugging
    _input_registers = register.registers

    register = client.read_holding_registers(
        0x0200, count=16
    )  # hub.count_bits_analog_out / 16
    # Store register values for debugging
    _holding_registers = register.registers

    register = client.read_input_registers(
        0x0024, count=10
    )  # hub.count_bits_digital_in / 16
    # Store register values for debugging
    _input_registers_binary = [format(i, "016b") for i in register.registers]

    register = client.read_discrete_inputs(
        0x0000, count=146
    )  # hub.count_bits_digital_in
    # Store register values for debugging
    _discrete_inputs = register.bits

    register = client.read_coils(
        0x0200, count=80
    )  # hub.count_bits_digital_out
    # Store register values for debugging
    _coils = register.bits


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_count_analog(hub: Hub) -> None:
    """Test counting analog modules."""
    assert len(hub.get_digital_modules()) == 36, (
        f"Error: expected 12 digital modules, got {len(hub.get_digital_modules())}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_count_digital(hub: Hub) -> None:
    """Test counting digital modules."""
    assert len(hub.get_analog_modules()) == 11, (
        f"Error: expected 11 analog modules, got {len(hub.get_analog_modules())}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_count_total(hub: Hub) -> None:
    """Test counting total modules."""
    assert len(hub.modules) == 47, (
        f"Error: expected 47 modules, got {len(hub.modules)}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_digital_input_bits_match(hub: Hub) -> None:
    """Test matching digital input bits."""
    digital_input_bits = sum(
        module.spec.modbus_channels["discrete"]
        for module in hub.get_digital_modules()
        if module.spec.io_type.input
    )
    assert digital_input_bits == 146, (
        f"Error: expected 146 digital input bits, got {digital_input_bits}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_digital_output_bits_match(hub: Hub) -> None:
    """Test matching digital output bits."""
    digital_outputs_bits = sum(
        module.spec.modbus_channels["coil"]
        for module in hub.get_digital_modules()
        if module.spec.io_type.output
    )
    assert digital_outputs_bits == 80, (
        f"Error: expected 80 digital output bits, got {digital_outputs_bits}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_analog_input_bits_match(hub: Hub) -> None:
    """Test matching analog input bits."""
    analog_inputs_bits = (
        sum(
            module.spec.modbus_channels["input"]
            for module in hub.get_analog_modules()
            if module.spec.io_type.input
        )
        * 16
    )
    assert analog_inputs_bits == 384, (
        f"Error: expected 384 analog input bits, got {analog_inputs_bits}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_module_analog_output_bits_match(hub: Hub) -> None:
    """Test matching analog output bits."""
    analog_outputs_bits = (
        sum(
            module.spec.modbus_channels["holding"]
            for module in hub.get_analog_modules()
            if module.spec.io_type.output
        )
        * 16
    )
    assert analog_outputs_bits == 256, (
        f"Error: expected 256 analog output bits, got {analog_outputs_bits}"
    )


@pytest.mark.skip(reason="Test needs physical PLC connection")
def test_channel_count_match_all_modules(hub: Hub) -> None:
    """Test matching channel counts for all modules."""
    for module in hub.modules:
        channels_spec = sum(module.spec.modbus_channels.values())
        channels_actual = sum(
            len(channels) for channels in module.modbus_channels.values()
        )
        assert channels_spec == channels_actual, (
            f"Error: expected {channels_spec} channels, got {channels_actual}"
        )


@pytest.mark.skip(reason="Test needs physical PLC connection")
@pytest.mark.parametrize(
    "module_idx,modbus_channel_type",
    [
        (352, "discrete"),
        (559, "holding"),
        (33794, "coil"),
        (36866, "coil"),
        (36865, "discrete"),
        (33793, "discrete"),
        (459, "input"),
        (453, "input"),
        (460, "input"),
        (451, "input"),
        (404, "input"),
        (33281, "discrete"),
    ],
)
def test_module_channel_type(
    hub: Hub, module_idx: int, modbus_channel_type: str
) -> None:
    """Test module channel types."""
    for channel in hub.modules[module_idx].modbus_channels[modbus_channel_type]:
        assert channel.channel_type == modbus_channel_type, (
            f"Error: expected {modbus_channel_type} channel, got {channel.channel_type}"
        )


@pytest.mark.skip(reason="Test needs physical PLC connection")
@pytest.mark.parametrize(
    "module_idx,modbus_channel_type,start_address",
    [
        (352, "discrete", 0x0000),
        (559, "holding", 0x0200),
        (33794, "coil", 0x0200),
        (36866, "coil", 0x0200),
        (36865, "discrete", 0x0000),
        (33793, "discrete", 0x0000),
        (459, "input", 0x0000),
        (453, "input", 0x0000),
        (460, "input", 0x0000),
        (451, "input", 0x0000),
        (404, "input", 0x0000),
        (33281, "discrete", 0x0000),
    ],
)
def test_module_addresses(
    hub: Hub, module_idx: int, modbus_channel_type: str, start_address: int
) -> None:
    """Test module addresses."""
    for index, channel in enumerate(
        hub.modules[module_idx].modbus_channels[modbus_channel_type]
    ):
        assert channel.address == start_address + index, (
            f"Error: expected address {start_address + index}, got {channel.address}"
        )
