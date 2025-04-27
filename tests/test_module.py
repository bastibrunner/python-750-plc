"""Tests for the Wago PLC module configuration."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument

from collections.abc import Generator

import pytest
from pytest_socket import enable_socket, socket_allow_hosts

from wg750xxx.modules.module import WagoModule
from wg750xxx.modules.spec import IOType
from wg750xxx.settings import HubConfig, ModuleConfig
from wg750xxx.wg750xxx import PLCHub


@pytest.fixture(scope="module")
def hub() -> Generator[PLCHub, None, None]:
    """Create a Hub instance for testing."""
    enable_socket()
    socket_allow_hosts(["10.22.22.16", "localhost", "::1"], allow_unix_socket=True)
    try:
        hub_instance = PLCHub(HubConfig(host="10.22.22.16", port=502), True)
        yield hub_instance
    except Exception as e:  # noqa: BLE001
        pytest.skip(
            f"Test skipped: Need physical PLC connection, but failed to create Hub instance: {e}"
        )


@pytest.fixture(scope="module")
def module_config(hub: PLCHub) -> list[ModuleConfig]:
    """Store module configuration for debugging."""
    return [i.config for i in hub.modules]


def test_read_register(hub: PLCHub) -> None:
    """Test reading registers."""
    client = hub._client  # noqa: SLF001
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

    register = client.read_coils(0x0200, count=80)  # hub.count_bits_digital_out
    # Store register values for debugging
    _coils = register.bits


def test_module_count(hub: PLCHub) -> None:
    """Test counting analog input modules."""
    modules = hub.modules.get(IOType(input=True))
    assert len(modules) == 5, (
        f"Error: expected 5 analog input modules, got {len(modules)}"
    )
    modules = hub.modules.get(IOType(output=True))
    assert isinstance(modules, WagoModule), (
        f"Error: expected 1 analog output modules, got {len(modules)}"
    )
    modules = hub.modules.get(IOType(digital=True, input=True))
    assert len(modules) == 19, (
        f"Error: expected 19 digital input modules, got {len(modules)}"
    )
    modules = hub.modules.get(IOType(digital=True, output=True))
    assert len(modules) == 17, (
        f"Error: expected 17 digital output modules, got {len(modules)}"
    )


def test_module_count_total(hub: PLCHub) -> None:
    """Test counting total modules."""
    assert len(hub.modules) == 47, f"Error: expected 47 modules, got {len(hub.modules)}"


def test_module_digital_input_bits_match(hub: PLCHub) -> None:
    """Test matching digital input bits."""
    digital_input_bits = sum(
        module.spec.modbus_channels["discrete"]
        for module in hub.modules.get(IOType(digital=True, input=True))
        if module.spec.io_type.input
    )
    assert digital_input_bits == 146, (
        f"Error: expected 146 digital input bits, got {digital_input_bits}"
    )


def test_module_digital_output_bits_match(hub: PLCHub) -> None:
    """Test matching digital output bits."""
    digital_outputs_bits = sum(
        module.spec.modbus_channels["coil"]
        for module in hub.modules.get(IOType(digital=True, output=True))
        if module.spec.io_type.output
    )
    assert digital_outputs_bits == 80, (
        f"Error: expected 80 digital output bits, got {digital_outputs_bits}"
    )


def test_module_analog_input_bits_match(hub: PLCHub) -> None:
    """Test matching analog input bits."""
    analog_inputs_bits = (
        sum(
            module.spec.modbus_channels["input"]
            for module in hub.modules.get(IOType(input=True))
            if module.spec.io_type.input
        )
        * 16
    )
    assert analog_inputs_bits == 384, (
        f"Error: expected 384 analog input bits, got {analog_inputs_bits}"
    )


def test_module_analog_output_bits_match(hub: PLCHub) -> None:
    """Test matching analog output bits."""
    analog_outputs_bits = (
        sum(
            module.spec.modbus_channels["holding"]
            for module in [hub.modules.get(IOType(output=True))]
            if module.spec.io_type.output
        )
        * 16
    )
    assert analog_outputs_bits == 64, (
        f"Error: expected 64 analog output bits, got {analog_outputs_bits}"
    )


def test_channel_count_match_all_modules(hub: PLCHub) -> None:
    """Test matching channel counts for all modules."""
    for module in hub.modules:
        channels_spec = sum(module.spec.modbus_channels.values())
        channels_actual = sum(
            len(channels) for channels in module.modbus_channels.values()
        )
        assert channels_spec == channels_actual, (
            f"Error: expected {channels_spec} channels, got {channels_actual}"
        )


def test_module_counter_count(hub: PLCHub) -> None:
    """Test counter count."""
    modules = hub.modules.get("404")
    assert modules is not None, "Counter modules should be present"
    assert isinstance(modules, list) and len(modules) == 3, (
        f"Error: expected 3 counter modules, got {len(modules)}"
    )
    for module in modules:
        assert module.channels[0].channel_type == "Counter 32Bit", (
            f"Error: expected Counter 32Bit channel, got {module.channels[0].channel_type}"
        )
        value = module.channels[0].read()
        assert isinstance(value, int)


@pytest.mark.parametrize(
    ("module_idx", "modbus_channel_type"),
    [
        (1, "Int16 Out"),
        (2, "Digital Out"),
        (3, "Digital Out"),
        (4, "Digital Out"),
        (5, "Digital Out"),
        (6, "Digital Out"),
        (7, "Digital Out"),
        (8, "Digital Out"),
        (9, "Digital Out"),
        (10, "Digital Out"),
        (11, "Digital Out"),
        (12, "Digital Out"),
        (13, "Digital Out"),
        (14, "Digital Out"),
        (15, "Digital Out"),
        (16, "Digital Out"),
        (17, "Digital Out"),
        (18, "Digital Out"),
        (19, "Digital In"),
        (20, "Digital In"),
        (21, "Digital In"),
        (22, "Digital In"),
        (23, "Digital In"),
        (24, "Digital In"),
        (25, "Digital In"),
        (26, "Digital In"),
        (27, "Digital In"),
        (28, "Digital In"),
        (29, "Digital In"),
        (30, "Digital In"),
        (31, "Digital In"),
        (32, "Digital In"),
        (33, "Int16 In"),
        (34, "Int16 In"),
        (35, "Int16 In"),
        (36, "Int16 In"),
        (37, "Int16 In"),
        (38, "Counter 32Bit"),
        (39, "Counter 32Bit"),
        (40, "Counter 32Bit"),
        (41, "Digital In"),
        (42, "Digital In"),
        (43, "Digital In"),
        (44, "Digital In"),
        (45, "Digital In"),
        (46, "Dali"),
    ],
)
def test_module_channel_type(
    hub: PLCHub, module_idx: int, modbus_channel_type: str
) -> None:
    """Test module channel types."""
    for channel in hub.modules[module_idx].channels:
        assert channel.channel_type == modbus_channel_type, (
            f"Error: expected {modbus_channel_type} channel, got {channel.channel_type}"
        )


@pytest.mark.parametrize(
    ("module_idx", "modbus_channel_type", "start_address"),
    [
        (1, "holding", 0x0000),
        (2, "coil", 0x0000),
        (3, "coil", 0x0004),
        (4, "coil", 0x0008),
        (5, "coil", 0x000C),
        (6, "coil", 0x0010),
        (7, "coil", 0x0014),
        (8, "coil", 0x0018),
        (9, "coil", 0x001C),
    ],
)
def test_module_addresses(
    hub: PLCHub, module_idx: int, modbus_channel_type: str, start_address: int
) -> None:
    """Test module addresses."""
    for index, channel in enumerate(
        hub.modules[module_idx].modbus_channels[modbus_channel_type]
    ):
        assert channel.address == start_address + index, (
            f"Error: expected address {start_address + index}, got {channel.address}"
        )
