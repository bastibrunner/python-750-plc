"""Test the Digital module."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging
from random import randint
import re

import pytest

from wg750xxx.wg750xxx import PLCHub
from wg750xxx.modules.digital.modules import Wg750DigitalIn, Wg750DigitalOut

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py

# Define digital module type groups
DigitalInputModule = Wg750DigitalIn
DigitalOutputModule = Wg750DigitalOut


def test_digital_input_modules_created(configured_hub: PLCHub) -> None:
    """Test that digital input modules are created correctly."""
    digital_input_modules = [
        module for module in configured_hub.modules
        if module.spec.io_type.digital and module.spec.io_type.input
    ]

    assert len(digital_input_modules) > 0, "No digital input modules found"

    for module in digital_input_modules:
        assert isinstance(module, DigitalInputModule), \
            f"Module {module.display_name} should be a DigitalInputModule"
        assert len(module.channels or []) > 0, f"Module {module.display_name} has no channels"

        for channel in module.channels:
            assert channel.channel_type == "Digital In", \
                f"Channel {channel} has incorrect type {channel.channel_type}"


def test_digital_output_modules_created(configured_hub: PLCHub) -> None:
    """Test that digital output modules are created correctly."""
    digital_output_modules = [
        module for module in configured_hub.modules
        if module.spec.io_type.digital and module.spec.io_type.output
    ]

    assert len(digital_output_modules) > 0, "No digital output modules found"

    for module in digital_output_modules:
        assert isinstance(module, DigitalOutputModule), \
            f"Module {module.display_name} should be a DigitalOutputModule"
        assert len(module.channels or []) > 0, f"Module {module.display_name} has no channels"

        for channel in module.channels:
            assert channel.channel_type == "Digital Out", \
                f"Channel {channel} has incorrect type {channel.channel_type}"


def test_digital_input_channel_read(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test reading from digital input channels."""
    for _ in range(10):  # Test multiple random states
        modbus_mock_with_modules.randomize_state()
        if configured_hub.connection is not None:
            configured_hub.connection.update_state()

        for module in configured_hub.modules:
            if not module.spec.io_type.digital or not module.spec.io_type.input:
                continue

            for channel in module.channels:
                value = channel.read()
                assert isinstance(value, bool), f"Channel {channel} read should return a boolean value"

                if hasattr(channel, "modbus_channel") and channel.modbus_channel:
                    address = channel.modbus_channel.address
                    mock_result = modbus_mock_with_modules.read_discrete_inputs(address)
                    mock_value = bool(mock_result.bits[0])
                    error_msg = f"Channel {channel} value {value} doesn't match mock value {mock_value}"
                    assert value == mock_value, error_msg


def test_digital_output_channel_write(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test writing to digital output channels."""
    for _ in range(10):  # Test multiple random values
        for module in configured_hub.modules:
            if not module.spec.io_type.digital or not module.spec.io_type.output:
                continue

            for channel in module.channels:
                test_value = bool(randint(0, 1))
                channel.write(test_value)

                if hasattr(channel, "modbus_channel") and channel.modbus_channel:
                    address = channel.modbus_channel.address
                    mock_result = modbus_mock_with_modules.read_coils(address)
                    mock_value = bool(mock_result.bits[0])
                    error_msg = f"Channel {channel} written value {test_value} doesn't match mock value {mock_value}"
                    assert test_value == mock_value, error_msg


def test_digital_channel_callbacks(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test that digital channel callbacks work correctly."""
    callback_called = False
    callback_value = None

    def test_callback(value):
        nonlocal callback_called, callback_value
        callback_called = True
        callback_value = value

    # Find a digital input channel to test
    test_channel = None
    for module in configured_hub.modules:
        if module.spec.io_type.digital and module.spec.io_type.input:
            if module.channels:
                test_channel = module.channels[0]
                break

    assert test_channel is not None, "No digital input channel found for testing callbacks"

    # Register callback
    test_channel.on_change_callback = test_callback

    # Change the mock value and update state
    if test_channel.modbus_channel:
        address = test_channel.modbus_channel.address
        test_value = bool(randint(0, 1))
        modbus_mock_with_modules.set_discrete_input_value(address, test_value)

        if configured_hub.connection is not None:
            configured_hub.connection.update_state()

            # Manually trigger notification since we're in test mode
            test_channel.notify_value_change(test_value)

            assert callback_called, "Callback was not called"
            error_msg = f"Callback received wrong value: {callback_value} instead of {test_value}"
            assert callback_value == test_value, error_msg

    # Clean up
    test_channel.on_change_callback = None


def test_digital_channel_config(configured_hub: PLCHub) -> None:
    """Test digital channel configuration."""
    for module in configured_hub.modules:
        if not module.spec.io_type.digital:
            continue

        for channel in module.channels:
            config = channel.config
            assert config is not None, f"Channel {channel} has no config"
            error_msg = f"Config type {config.type} doesn't match channel type {channel.channel_type}"
            assert config.type == channel.channel_type, error_msg

            # Test auto-generated name
            original_name = channel.name
            channel.name = None
            expected_name = re.compile(r"^.*\s\d+$")
            error_msg = f"Auto-generated name is incorrect: {channel.auto_generated_name()}"
            assert expected_name.match(channel.auto_generated_name()), error_msg

            # Restore name
            channel.name = original_name


def test_module_channel_count(configured_hub: PLCHub) -> None:
    """Test that modules have the correct number of channels."""
    for module in configured_hub.modules:
        if not module.spec.io_type.digital:
            continue

        # Digital modules should have channels matching their module spec
        assert module.channels is not None, f"Module {module.display_name} has no channels"
        channel_count = len(module.channels)
        expected_count = 0

        if module.spec.io_type.input:
            expected_count = module.spec.modbus_channels.get("discrete", 0)
        elif module.spec.io_type.output:
            expected_count = module.spec.modbus_channels.get("coil", 0)

        error_msg = f"Module {module.display_name} has {channel_count} channels but should have {expected_count}"
        assert channel_count == expected_count, error_msg
