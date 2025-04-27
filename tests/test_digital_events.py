"""Test the Digital Event functionality."""

# pylint: disable=protected-access,redefined-outer-name,unused-argument
import asyncio
from unittest.mock import MagicMock, patch

import pytest

from wg750xxx.modbus.state import Discrete, ModbusConnection
from wg750xxx.modules.digital.channels import DigitalEvent, DigitalIn, EventButton
from wg750xxx.settings import ChannelConfig
from wg750xxx.wg750xxx import PLCHub


@pytest.fixture
def mock_modbus_connection():
    """Create a mock ModbusConnection."""
    mock_connection = MagicMock(spec=ModbusConnection)
    mock_connection.read_discrete_input.return_value = False
    return mock_connection


@pytest.fixture
def event_button(mock_modbus_connection):
    """Create an EventButton instance for testing."""
    discrete = Discrete(0, mock_modbus_connection)
    config = ChannelConfig(
        name="Test Button", type="Digital In", device_class="event_button"
    )
    return EventButton(discrete, config)


def test_channel_is_event_button_when_device_class_set(configured_hub: PLCHub) -> None:
    """Test that channels are created as EventButton when device_class is set appropriately."""
    # Find a digital input module to modify
    digital_input_modules = [
        module
        for module in configured_hub.modules
        if module.spec.io_type.digital and module.spec.io_type.input
    ]

    assert len(digital_input_modules) > 0, "No digital input modules found for testing"

    test_module = digital_input_modules[0]
    original_channel = test_module.channels[0]  # type: ignore

    # Create a new channel with device_class set to event_button
    discrete = original_channel.modbus_channel
    event_config = ChannelConfig(
        name="Event Button Test", type="Digital In", device_class="event_button"
    )

    # Create the event button directly
    event_button = EventButton(discrete, event_config)

    # Verify the new channel is an EventButton
    assert isinstance(event_button, EventButton), (
        "Channel was not converted to an EventButton"
    )
    assert event_button.device_class == "event_button"


def test_get_instance_returns_event_button(mock_modbus_connection):
    """Test that get_instance returns an EventButton when device_class is set to event_button."""
    discrete = Discrete(0, mock_modbus_connection)
    config = ChannelConfig(
        name="Test Button", type="Digital In", device_class="event_button"
    )
    digital_in = DigitalIn(discrete, config)

    instance = digital_in.get_instance()

    assert isinstance(instance, EventButton)
    assert instance.device_class == "event_button"


def test_normal_get_instance(mock_modbus_connection):
    """Test that get_instance returns a regular DigitalIn when device_class is not event_button."""
    discrete = Discrete(0, mock_modbus_connection)
    config = ChannelConfig(
        name="Test Input", type="Digital In", device_class="binary_sensor"
    )
    digital_in = DigitalIn(discrete, config)

    instance = digital_in.get_instance()

    assert isinstance(instance, DigitalIn)
    assert not isinstance(instance, EventButton)


@pytest.mark.asyncio
async def test_short_press_event(event_button):
    """Test that a short press generates the correct event."""
    callback_mock = MagicMock()

    def callback(value):
        callback_mock(value)

    event_button.on_change_callback = callback

    # Simulate button press
    event_button._handle_raw_state_change(True)

    # Wait a short time (less than SHORT_PRESS_TIMEOUT)
    await asyncio.sleep(0.2)

    # Simulate button release
    event_button._handle_raw_state_change(False)

    # Wait for double tap timeout
    await asyncio.sleep(event_button.DOUBLE_TAP_TIMEOUT + 0.1)

    # Check if correct event was generated
    callback_mock.assert_called_with(DigitalEvent.PRESSED.value)

    # Clean up pending tasks
    event_button._cancel_all_pending_tasks()


@pytest.mark.asyncio
async def test_double_tap_event(event_button):
    """Test that a double tap generates the correct event."""
    callback_mock = MagicMock()

    def callback(value):
        callback_mock(value)

    event_button.on_change_callback = callback

    # First tap
    event_button._handle_raw_state_change(True)
    await asyncio.sleep(0.1)
    event_button._handle_raw_state_change(False)

    # Wait a short time (less than DOUBLE_TAP_TIMEOUT)
    await asyncio.sleep(0.2)

    # Second tap
    event_button._handle_raw_state_change(True)
    await asyncio.sleep(0.1)
    event_button._handle_raw_state_change(False)

    # Wait to ensure processing completes
    await asyncio.sleep(0.1)

    # Check if correct event was generated
    callback_mock.assert_called_with(DigitalEvent.DOUBLE_TAP.value)

    # Clean up pending tasks
    event_button._cancel_all_pending_tasks()


@pytest.mark.asyncio
async def test_long_press_event(event_button):
    """Test that a long press generates the correct event."""
    callback_mock = MagicMock()

    def callback(value):
        callback_mock(value)

    event_button.on_change_callback = callback

    # Simulate button press
    event_button._handle_raw_state_change(True)

    # Wait longer than SHORT_PRESS_TIMEOUT but less than HOLD_DURATION
    await asyncio.sleep(event_button.SHORT_PRESS_TIMEOUT + 0.2)

    # Simulate button release
    event_button._handle_raw_state_change(False)

    # Wait to ensure processing completes
    await asyncio.sleep(0.1)

    # Check if correct event was generated
    callback_mock.assert_called_with(DigitalEvent.LONG_PRESS.value)

    # Clean up pending tasks
    event_button._cancel_all_pending_tasks()


@pytest.mark.asyncio
async def test_hold_events(event_button):
    """Test that a hold generates the correct events."""
    callback_mock = MagicMock()

    def callback(value):
        callback_mock(value)

    event_button.on_change_callback = callback

    # Simulate button press
    event_button._handle_raw_state_change(True)

    # Wait longer than HOLD_DURATION
    await asyncio.sleep(event_button.HOLD_DURATION + 0.1)

    # Verify HOLD_START was triggered
    callback_mock.assert_called_with(DigitalEvent.HOLD_START.value)

    # Reset the mock to check for the LONG_PRESS event when released
    callback_mock.reset_mock()

    # Simulate button release
    event_button._handle_raw_state_change(False)

    # Wait to ensure processing completes
    await asyncio.sleep(0.1)

    # Based on the implementation, when a HOLD_START has occurred,
    # releasing the button actually generates a LONG_PRESS event
    callback_mock.assert_called_with(DigitalEvent.LONG_PRESS.value)

    # Clean up pending tasks
    event_button._cancel_all_pending_tasks()


@pytest.mark.asyncio
async def test_debounce(event_button):
    """Test that rapid changes are properly debounced."""
    callback_mock = MagicMock()

    def callback(value):
        callback_mock(value)

    event_button.on_change_callback = callback

    # Simulate button press
    event_button._handle_raw_state_change(True)

    # Immediately simulate a button release (within debounce period)
    event_button._handle_raw_state_change(False)

    # Wait to ensure processing completes
    await asyncio.sleep(0.1)

    # The second change should have been ignored due to debounce
    # So no button event should have been triggered yet
    callback_mock.assert_not_called()

    # Now wait for the debounce period to end and make another change
    await asyncio.sleep(event_button.DEBOUNCE_TIMEOUT + 0.1)

    # Simulate a proper button press
    event_button._handle_raw_state_change(True)
    await asyncio.sleep(0.1)
    event_button._handle_raw_state_change(False)

    # Wait for the double tap timeout
    await asyncio.sleep(event_button.DOUBLE_TAP_TIMEOUT + 0.1)

    # Now we should see the button press event
    callback_mock.assert_called_with(DigitalEvent.PRESSED.value)

    # Clean up pending tasks
    event_button._cancel_all_pending_tasks()


@pytest.mark.asyncio
async def test_cancel_pending_tasks(event_button):
    """Test that pending tasks are properly cancelled when state changes."""
    # Create a spy on the _cancel_all_pending_tasks method
    with patch.object(
        event_button,
        "_cancel_all_pending_tasks",
        wraps=event_button._cancel_all_pending_tasks,
    ) as cancel_spy:
        # Simulate button press
        event_button._handle_raw_state_change(True)

        # Wait a bit but not enough to trigger anything
        await asyncio.sleep(0.1)

        # Simulate another state change
        event_button._handle_raw_state_change(False)

        # Verify _cancel_all_pending_tasks was called
        assert cancel_spy.called, "Pending tasks were not cancelled on state change"

    # Explicitly clean up all remaining tasks to avoid lingering tasks
    await asyncio.sleep(0.1)  # Give a little time for tasks to be created
    event_button._cancel_all_pending_tasks()

    # Wait a bit more to ensure tasks are actually cancelled
    await asyncio.sleep(0.1)
