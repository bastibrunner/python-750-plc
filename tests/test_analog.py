"""Test the Analog module."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging
from random import randint
import re
from wg750xxx.hub import Hub
from wg750xxx.modules.analog.modules import (
    Wg750AnalogIn1Ch, Wg750AnalogIn2Ch, Wg750AnalogIn4Ch, Wg750AnalogIn8Ch,
    Wg750AnalogOut2Ch, Wg750AnalogOut4Ch
)

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Using fixtures from conftest.py

# Define analog module type groups
AnalogInputModuleTypes = (Wg750AnalogIn1Ch, Wg750AnalogIn2Ch, Wg750AnalogIn4Ch, Wg750AnalogIn8Ch)
AnalogOutputModuleTypes = (Wg750AnalogOut2Ch, Wg750AnalogOut4Ch)


def test_analog_input_modules_created(configured_hub: Hub) -> None:
    """Test that analog input modules are created correctly."""
    analog_input_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AI1", "AI2", "AI4", "AI8", "AI16"]
    ]

    assert len(analog_input_modules) > 0, "No analog input modules found"

    for module in analog_input_modules:
        assert any(isinstance(module, cls) for cls in AnalogInputModuleTypes), \
            f"Module {module.display_name} should be an Analog Input Module"
        assert len(module.channels or []) > 0, f"Module {module.display_name} has no channels"

        for channel in module.channels:
            assert channel.channel_type in ["Int8 In", "Int16 In", "Float16 In"], \
                f"Channel {channel} has incorrect type {channel.channel_type}"


def test_analog_output_modules_created(configured_hub: Hub) -> None:
    """Test that analog output modules are created correctly."""
    analog_output_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AO1", "AO2", "AO4", "AO8", "AO16"]
    ]

    assert len(analog_output_modules) > 0, "No analog output modules found"

    for module in analog_output_modules:
        assert any(isinstance(module, cls) for cls in AnalogOutputModuleTypes), \
            f"Module {module.display_name} should be an Analog Output Module"
        assert len(module.channels or []) > 0, f"Module {module.display_name} has no channels"

        for channel in module.channels:
            assert channel.channel_type in ["Int8 Out", "Int16 Out", "Float16 Out"], \
                f"Channel {channel} has incorrect type {channel.channel_type}"


def test_analog_input_channel_read(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: Hub
) -> None:
    """Test reading from analog input channels."""
    analog_input_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AI1", "AI2", "AI4", "AI8"]
    ]
    tested_channels = 0
    for _ in range(10):  # Test multiple random states
        modbus_mock_with_modules.randomize_state()
        if configured_hub.connection is not None:
            configured_hub.connection.update_state()

        for module in analog_input_modules:
            for channel in module.channels:
                value = channel.read()
                assert value is not None, f"Channel {channel} read returned None"

                if hasattr(channel, "modbus_channel") and channel.modbus_channel:
                    address = channel.modbus_channel.address
                    mock_result = modbus_mock_with_modules.read_input_registers(address)
                    mock_value = mock_result.registers[0]
                    error_msg = f"Channel {channel} value {value} doesn't match mock value {mock_value}"
                    assert value == mock_value, error_msg
                    tested_channels += 1

    assert tested_channels > 0, "No analog input channels could be tested"



def test_analog_output_channel_write(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: Hub
) -> None:
    """Test writing to analog output channels."""
    analog_output_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AO1", "AO2", "AO4", "AO8"]
    ]
    tested_channels = 0
    for _ in range(10):  # Test multiple random values
        for module in analog_output_modules:
            for channel in module.channels:
                test_value = randint(0, 65535)  # Random value in 16-bit range
                channel.write(test_value)

                if hasattr(channel, "modbus_channel") and channel.modbus_channel:
                    address = channel.modbus_channel.address
                    mock_result = modbus_mock_with_modules.read_holding_registers(address)
                    mock_value = mock_result.registers[0]
                    error_msg = f"Channel {channel} written value {test_value} doesn't match mock value {mock_value}"
                    assert test_value == mock_value, error_msg
                    tested_channels += 1

    assert tested_channels > 0, "No analog output channels could be tested"


def test_analog_channel_callbacks(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: Hub
) -> None:
    """Test that analog channel callbacks work correctly."""
    callback_called = False
    callback_value = None

    def test_callback(value):
        nonlocal callback_called, callback_value
        callback_called = True
        callback_value = value

    # Find an analog input channel to test
    test_channel = None
    for module in configured_hub.modules:
        if not module.spec.io_type.digital and module.spec.io_type.input:
            if module.channels:
                test_channel = module.channels[0]
                break

    assert test_channel is not None, "No analog input channel found for testing callbacks"

    # Register callback
    test_channel.on_change_callback = test_callback

    # Change the mock value and update state
    if test_channel.modbus_channel:
        address = test_channel.modbus_channel.address
        test_value = randint(0, 65535)
        modbus_mock_with_modules.set_holding_register_value(address, test_value)

        if configured_hub.connection is not None:
            configured_hub.connection.update_state()

            # Manually trigger notification since we're in test mode
            test_channel.notify_value_change(test_value)

            assert callback_called, "Callback was not called"
            error_msg = f"Callback received wrong value: {callback_value} instead of {test_value}"
            assert callback_value == test_value, error_msg

    # Clean up
    test_channel.on_change_callback = None


def test_analog_channel_config(configured_hub: Hub) -> None:
    """Test analog channel configuration."""

    analog_input_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AI1", "AI2", "AI4", "AI8", "AI16"]
    ]

    analog_output_modules = [
        module for module in configured_hub.modules
        if module.display_name in ["AO1", "AO2", "AO4", "AO8", "AO16"]
    ]

    for module in analog_input_modules + analog_output_modules:

        assert module.channels is not None, f"Module {module} has no channels"

        for channel in module.channels:
            config = channel.config
            assert config is not None, f"Channel {channel} has no config"
            error_msg = f"Config type {config.type} doesn't match channel type {channel.channel_type}"
            assert config.type == channel.channel_type, error_msg

            # Test auto-generated name
            original_name = channel.name
            channel.name = None
            expected_name = re.compile(r"Int\d+ (In|Out) \d+")
            error_msg = f"Auto-generated name is incorrect: {channel.auto_generated_name()}"
            assert expected_name.match(channel.auto_generated_name()), error_msg

            # Restore name
            channel.name = original_name
