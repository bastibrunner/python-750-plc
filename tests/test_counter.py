"""Test the Counter module."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import logging
from random import randint
import re

import pytest

from wg750xxx.modules.counter.modules import Wg750Counter
from wg750xxx.wg750xxx import PLCHub

from .mock.mock_modbus_tcp_client import MockModbusTcpClient

logger = logging.getLogger(__name__)

# Define counter module type group
CounterModuleTypes = (Wg750Counter,)


def test_counter_modules_created(configured_hub: PLCHub) -> None:
    """Test that counter modules are created correctly."""
    # Find counter modules based on their aliases (typically include "counter")
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    # If no counter modules found by alias, this test will be skipped
    for module in counter_modules:
        assert any(isinstance(module, cls) for cls in CounterModuleTypes), (
            f"Module {module.display_name} should be a Counter Module"
        )
        assert module.channels is not None, (
            f"Module {module.display_name} has no channels"
        )
        assert len(module.channels) > 0, f"Module {module.display_name} has no channels"
        for channel in module.channels:
            assert channel.channel_type in ["Counter 16Bit", "Counter 32Bit"], (
                f"Channel {channel} has incorrect type {channel.channel_type}"
            )


def test_counter_channel_read(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test reading from counter channels."""
    # Find counter modules
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    if not counter_modules:
        pytest.skip("No counter modules found in the configured hub")

    for _ in range(5):  # Test multiple random states
        modbus_mock_with_modules.randomize_state()
        if configured_hub.connection is not None:
            configured_hub.connection.update_state()

        for module in counter_modules:
            assert module.channels is not None, f"Module {module} has no channels"
            for channel in module.channels:
                value = channel.read()
                assert value is not None, f"Channel {channel} read returned None"

                # For counter modules, the read operation might use multiple modbus addresses
                # depending on if it's 16-bit or 32-bit, so detailed verification
                # would need to be customized based on the specific implementation


@pytest.mark.skip(
    reason="Skipping counter reset test, it's not implemented in modbus_mock"
)
def test_counter_channel_reset(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test counter reset functionality if available."""
    # Find counter modules
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    if not counter_modules:
        pytest.skip("No counter modules found in the configured hub")

    for module in counter_modules:
        assert module.channels is not None, f"Module {module} has no channels"
        for channel in module.channels:
            # Check if the channel has a reset method
            if hasattr(channel, "reset") and callable(channel.reset):
                # Before reset, read the current value
                before_value = channel.read()
                assert before_value is not None, (
                    f"Channel {channel} has no value before reset"
                )
                assert before_value != 0, (
                    f"Channel {channel} value before reset is not an integer"
                )
                # Call reset
                channel.reset()

                # After reset, the value should be 0 (or whatever the reset value is)
                after_value = channel.read()
                assert after_value == 0, (
                    f"Channel {channel} value after reset should be 0, got {after_value}"
                )


def test_counter_channel_callbacks(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test that counter channel callbacks work correctly."""
    # Find counter modules
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    if not counter_modules:
        pytest.skip("No counter modules found in the configured hub")

    callback_called = False
    callback_value = None

    def test_callback(value) -> None:
        nonlocal callback_called, callback_value
        callback_called = True
        callback_value = value

    # Find a counter channel to test
    test_channel = None
    for module in counter_modules:
        if module.channels:
            test_channel = module.channels[0]
            break

    assert test_channel is not None, "No counter channel found for testing callbacks"

    # Register callback
    test_channel.on_change_callback = test_callback

    # Manually trigger notification since we're in test mode
    test_value = randint(0, 65535)
    test_channel.notify_value_change(test_value)

    assert callback_called, "Callback was not called"
    error_msg = (
        f"Callback received wrong value: {callback_value} instead of {test_value}"
    )
    assert callback_value == test_value, error_msg

    # Clean up
    test_channel.on_change_callback = None


def test_counter_channel_config(configured_hub: PLCHub) -> None:
    """Test counter channel configuration."""
    # Find counter modules
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    if not counter_modules:
        pytest.skip("No counter modules found in the configured hub")

    for module in counter_modules:
        assert module.channels is not None, f"Module {module} has no channels"
        for channel in module.channels:
            config = channel.config
            assert config is not None, f"Channel {channel} has no config"
            error_msg = f"Config type {config.type} doesn't match channel type {channel.channel_type}"
            assert config.type == channel.channel_type, error_msg

            # Test auto-generated name
            expected_name = re.compile(r"Counter \d+Bit \d+")
            assert expected_name.match(channel.auto_generated_name()), (
                f"Auto-generated name is incorrect: {channel.auto_generated_name()}"
            )


def test_32bit_counter_values(
    modbus_mock_with_modules: MockModbusTcpClient, configured_hub: PLCHub
) -> None:
    """Test 32-bit counter values if available."""
    # Find counter modules
    counter_modules = [
        module
        for module in configured_hub.modules
        if any("404" in alias.lower() for alias in module.aliases)
    ]

    if not counter_modules:
        pytest.skip("No counter modules found in the configured hub")

    for module in counter_modules:
        assert module.channels is not None
        for channel in module.channels:
            assert channel is not None
            if channel.channel_type == "Counter 32Bit":
                # For 32-bit counters, test large values that would require 32 bits
                if hasattr(channel, "modbus_channel") and channel.modbus_channel:
                    # Read current value
                    initial_value = channel.read()
                    error_msg = (
                        f"Counter value should be an integer, got {type(initial_value)}"
                    )
                    assert isinstance(initial_value, int), error_msg
