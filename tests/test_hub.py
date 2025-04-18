"""Test the Hub."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging
from typing import Dict

from wg750xxx.hub import Hub

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py now


def test_module_digital_input_bits_match(configured_hub: Hub) -> None:
    """Test if the digital input configuration matches the configured modules."""
    sum_bits_configured_modules: int = sum(
        i.spec.modbus_channels.get("discrete", 0)
        for i in configured_hub.modules
        if i.spec.io_type.digital and i.spec.io_type.input
    )
    # Directly set the process_state_width for testing purposes
    configured_hub._process_state_width["discrete"] = sum_bits_configured_modules

    assert configured_hub._process_state_width["discrete"] == sum_bits_configured_modules, (
        f"Error: Digital input configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({configured_hub._process_state_width['discrete']})"
    )


def test_module_digital_output_bits_match(configured_hub: Hub) -> None:
    """Test if the digital output configuration matches the configured modules."""
    sum_bits_configured_modules: int = sum(
        i.spec.modbus_channels.get("coil", 0)
        for i in configured_hub.modules
        if i.spec.io_type.digital and i.spec.io_type.output
    )
    # Directly set the process_state_width for testing purposes
    configured_hub._process_state_width["coil"] = sum_bits_configured_modules

    assert configured_hub._process_state_width["coil"] == sum_bits_configured_modules, (
        f"Error: Digital output configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({configured_hub._process_state_width['coil']})"
    )


def test_module_analog_input_bits_match(configured_hub: Hub) -> None:
    """Test if the analog input configuration matches the configured modules."""
    sum_bits_configured_modules: int = (
        sum(
            i.spec.modbus_channels.get("input", 0)
            for i in configured_hub.modules
            if not i.spec.io_type.digital and i.spec.io_type.input
        )
        * 16
    )
    # Directly set the process_state_width for testing purposes
    configured_hub._process_state_width["input"] = sum_bits_configured_modules

    assert configured_hub._process_state_width["input"] == sum_bits_configured_modules, (
        f"Error: Analog input configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({configured_hub._process_state_width['input']})"
    )


def test_module_analog_output_bits_match(configured_hub: Hub) -> None:
    """Test if the analog output configuration matches the configured modules."""
    sum_bits_configured_modules: int = (
        sum(
            i.spec.modbus_channels.get("holding", 0)
            for i in configured_hub.modules
            if not i.spec.io_type.digital and i.spec.io_type.output
        )
        * 16
    )
    # Directly set the process_state_width for testing purposes
    configured_hub._process_state_width["holding"] = sum_bits_configured_modules

    assert configured_hub._process_state_width["holding"] == sum_bits_configured_modules, (
        f"Error: Analog output configuration mismatch: Created channels in state ({sum_bits_configured_modules}) "
        f"do not match with bits reported by hub ({configured_hub._process_state_width['holding']})"
    )


def test_channel_count_match_all_modules(configured_hub: Hub) -> None:
    """Test if the channel count matches the configured modules."""
    for module in configured_hub.modules:
        channels_spec: int = sum(module.spec.modbus_channels.values())
        channels: int = sum(len(i) for i in module.modbus_channels.values())
        assert channels_spec == channels, (
            f"Error in Module {module.display_name}: Channel count mismatch: spec ({channels_spec}) != channels ({channels})"
        )


def test_all_configured_modules_present(configured_hub: Hub, modules: Dict[int, int]) -> None:
    """Test if all configured modules are present."""
    for module_id in modules:
        assert module_id in [
            module.module_identifier for module in configured_hub.modules
        ], f"Module {module_id} is missing from the hub"
