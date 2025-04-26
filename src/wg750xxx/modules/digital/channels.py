"""Basic channels for the Wago 750 series."""

import asyncio
from enum import Enum
import time
from typing import Any, Callable, Optional, Set, Self

from ...modbus.state import Coil, Discrete
from ..channel import WagoChannel
from ..exceptions import WagoModuleError



class DigitalIn(WagoChannel):
    """Digital Input."""

    platform: str = "binary_sensor"
    device_class: str = "binary_sensor"
    unit_of_measurement: str = ""
    icon: str = "mdi:binary"
    value_template: str = "{{ value | bool }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the digital input channel.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        Raises:
            ValueError: If the modbus_channel is not a Discrete.

        """
        super().__init__("Digital In", *args, **kwargs)
        if not isinstance(self.modbus_channel, Discrete):
            raise TypeError("modbus_channel must be a Discrete")

    def get_instance(self) -> Self | "EventButton":
        """Get an instance of the channel."""
        if self.config.device_class == "event_button":
            return EventButton(self.modbus_channel, self.config)
        else:
            return self

    def read(self) -> bool:
        """Read the state of the digital input channel."""
        if self.modbus_channel is None:
            raise WagoModuleError(f"Modbus channel not set for {self.name}")
        r = self.modbus_channel.read()
        if not isinstance(r, bool):
            raise WagoModuleError(f"Read value {r} is not a bool")
        return r

    def write(self, value: Any) -> None:
        """Write a value to the digital input channel.

        Raises:
            WagoModuleError: If the channel is an input channel.

        """
        raise WagoModuleError("Can not write to input channel")


class DigitalOut(WagoChannel):
    """Digital Output."""

    platform: str = "switch"
    device_class: str = "switch"
    unit_of_measurement: str = ""
    icon: str = "mdi:binary"
    value_template: str = "{{ value | bool }}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the digital output channel.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        Raises:
            ValueError: If the modbus_channel is not a Coil.

        """
        super().__init__("Digital Out", *args, **kwargs)
        if not isinstance(self.modbus_channel, Coil):
            raise TypeError("modbus_channel must be a Coil")

    def write(self, value: Any) -> None:
        """Write a value to the digital output channel."""
        self.modbus_channel.write(value)

    def read(self) -> bool | str:
        """Read the state of the digital output channel."""
        return self.modbus_channel.read()

class DigitalEvent(Enum):
    """Digital events."""

    DOUBLE_TAP = "double_tap"
    LONG_PRESS = "long_press"  # Changed from start/end to single event
    PRESSED = "pressed"
    HOLD_START = "hold_start"
    HOLD_END = "hold_end"



class EventButton(DigitalIn):
    """Button that detects different press patterns.

    This channel doesn't expose the raw binary state directly. Instead,
    it detects patterns like short press, long press, double tap, etc.,
    and exposes these as events.

    All buttons are monitored by a single shared async task for efficiency.
    """

    platform: str = "binary_sensor"
    device_class: str = "event_button"
    unit_of_measurement: str = ""
    icon: str = "mdi:gesture-tap-button"
    value_template: str = "{{ value }}"

    # Configuration constants
    DEBOUNCE_TIMEOUT = 0.05  # seconds to ignore rapid changes
    SHORT_PRESS_TIMEOUT = 0.5  # if the button is released before this time, it's a short press
    HOLD_DURATION = 0.8  # if the button is held for at least this long, it's a hold
    DOUBLE_TAP_TIMEOUT = 0.5  # if the button is pressed again within this time, it's a double tap

    def __init__(self, *args: Any, from_channel: DigitalIn|None = None, **kwargs: Any) -> None:
        """Initialize the event button channel."""
        if from_channel is None:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(from_channel.modbus_channel, from_channel.config, from_channel.channel_index, from_channel.on_change_callback)
        self._last_state: bool = False
        self._last_press_time: Optional[float] = None
        self._last_release_time: Optional[float] = None
        self._press_start_time: Optional[float] = None
        self._current_press_duration: float = 0
        self._last_event: Optional[DigitalEvent] = None
        self._raw_callback: Optional[Callable[[Any, Any | None], None]] = None
        self._last_state_change_time: float = 0
        self._pending_tasks: Set[asyncio.Task] = set()
        self._current_event: DigitalEvent | None = None
        self._pending_event: DigitalEvent | None = None

        # Register for raw state changes from the modbus channel
        if self.modbus_channel is not None:
            self.modbus_channel.modbus_connection.register_channel_callback(
                self.modbus_channel, self._handle_raw_state_change
            )


    def _handle_raw_state_change(self, value: bool) -> None:
        """Handle raw state changes from the modbus channel.

        This method implements the debounce logic and marks the button
        for state checking in the shared monitor.

        Args:
            value: The new binary state value
        """
        current_time = time.time()

        # Skip if change is too quick (debounce)
        if current_time - self._last_state_change_time < self.DEBOUNCE_TIMEOUT:
            return
        self._cancel_all_pending_tasks() # Cancel any pending tasks, since we're getting a new state change

        # Button was just pressed
        if value and not self._last_state:
            self._press_start_time = current_time
            self._current_press_duration = 0
            self._handle_press_start_event()

        # Button was just released
        elif not value and self._last_state:
            self._last_release_time = current_time
            self._current_press_duration = current_time - self._press_start_time
            self._handle_press_end_event()

        self._last_state_change_time = current_time
        self._last_state = value

    def _handle_press_start_event(self) -> None:
        """Handle the press start event."""
        task = asyncio.create_task(self._check_for_hold())
        self._pending_tasks.add(task)


    def _handle_press_end_event(self) -> None:
        """Handle the press end event."""
        if self._current_press_duration <= self.SHORT_PRESS_TIMEOUT:
            if self._pending_event is None:
                self._pending_event = DigitalEvent.DOUBLE_TAP
                task = asyncio.create_task(self._check_for_short_press())
                self._pending_tasks.add(task)
            elif self._pending_event == DigitalEvent.DOUBLE_TAP:
                self._pending_event = None
                self._trigger_event(DigitalEvent.DOUBLE_TAP)
            elif self._pending_event == DigitalEvent.HOLD_END:
                self._pending_event = None
                self._trigger_event(DigitalEvent.HOLD_END)
        else:
            self._trigger_event(DigitalEvent.LONG_PRESS)

    def _cancel_all_pending_tasks(self) -> None:
        """Cancel all pending tasks."""
        for task in self._pending_tasks:
            if not task.done():
                task.cancel()
        self._pending_tasks.clear()

    async def _check_for_short_press(self) -> None:
        """Check if button is held for long press duration."""
        try:
            await asyncio.sleep(self.DOUBLE_TAP_TIMEOUT)
            # If the sleep completed without being cancelled, there was no double tap, so it must be a short press
            self._trigger_event(DigitalEvent.PRESSED)
            self._pending_event = None
        except asyncio.CancelledError:
            pass

    async def _check_for_hold(self) -> None:
        """Check if button is held for hold duration."""
        try:
            await asyncio.sleep(self.HOLD_DURATION)
            # If the sleep completed without being cancelled, the button is still being held
            self._trigger_event(DigitalEvent.HOLD_START)
            self._pending_event = DigitalEvent.HOLD_END
        except asyncio.CancelledError:
            pass

    async def _wait_for_hold_end(self) -> None:
        """Wait for hold to end."""
        while self._last_state:
            await asyncio.sleep(0.1)  # Check periodically
        self._trigger_event(DigitalEvent.HOLD_END)


    def _trigger_event(self, event: DigitalEvent) -> None:
        """Trigger an event and call the callback.

        Args:
            event: The event to trigger
        """
        self._last_event = event
        if event in (DigitalEvent.PRESSED, DigitalEvent.DOUBLE_TAP):
            self._last_press_time = time.time()

        # Call the callback with the event value
        self.notify_value_change(event.value)

    @property
    def on_change_callback(self) -> Callable[[Any, Any | None], None] | None:
        """Get the callback function.

        Returns:
            The callback function or None if not set
        """
        return self._raw_callback

    @on_change_callback.setter
    def on_change_callback(self, callback: Callable[[Any, Any | None], None] | None) -> None:
        """Set the callback function that gets called when an event is detected.

        Args:
            callback: The callback function to set
        """
        self._raw_callback = callback

    def read(self) -> str | None:
        """Read the current event state.

        Returns:
            The current event state as string or empty string if no event
        """
        return self._last_event.value if self._last_event else None

    def notify_value_change(self, new_value: Any) -> None:
        if self.on_change_callback is None:
            return

        callback = self.on_change_callback

        # Call the callback directly without checking update interval
        if hasattr(callback, '__code__'):
            if callback.__code__.co_argcount == 1:
                callback(new_value)
            elif callback.__code__.co_argcount == 2:
                callback(new_value, self)
            else:
                raise ValueError(f"Callback function {callback.__name__} has {callback.__code__.co_argcount} arguments, expected 1 or 2")
