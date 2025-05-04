"""Module for handling Modbus communication and channel types for WAGO 750 series I/O modules."""

from abc import abstractmethod
from collections.abc import Callable, ItemsView
from functools import wraps
import logging
from threading import Thread
import time
from typing import Any, ClassVar, Literal, Optional, Self, cast, get_args

from pymodbus.client import ModbusTcpClient

from wg750xxx.const import DEFAULT_SCAN_INTERVAL

from .exceptions import ModbusCommunicationError
from .registers import Bits, Words

log = logging.getLogger(__name__)
ModbusChannelType = Literal["coil", "discrete", "input", "holding"]
ModbusBits = list[bool]
AddressDict = dict[ModbusChannelType, int]
ModbusChannelState = int | bool

class ModbusChannelSpec:
    """Class for representing the Modbus channel specification."""

    def __init__(self, spec: dict[ModbusChannelType, int] | None = None, **kwargs: int):
        """Initialize the ModbusChannelSpec.

        Args:
            spec: The Modbus channel specification as a dictionary.
            **kwargs: The Modbus channel specification as keyword arguments.

        """
        # Check if all keys in kwargs are in the ModbusChannelType enum
        if not all(key in get_args(ModbusChannelType) for key in kwargs):
            raise ValueError(f"Invalid channel type: {list(kwargs.keys())}")
        self._spec: dict[ModbusChannelType, int] = spec if spec is not None else cast(dict[ModbusChannelType, int],kwargs)

    def __getitem__(self, key: ModbusChannelType) -> int:
        """Get the number of channels for a specific type."""
        if key not in get_args(ModbusChannelType):
            raise ValueError(f"Invalid channel type: {key}")
        if key not in self._spec:
            return 0
        return self._spec[key]

    def __setitem__(self, key: ModbusChannelType, value: int) -> None:
        """Set the number of channels for a specific type."""
        if key not in get_args(ModbusChannelType):
            raise ValueError(f"Invalid channel type: {key}")
        self._spec[key] = value

    def __len__(self) -> int:
        """Get the total number of channels."""
        return self.channel_count()

    def get(self, key: ModbusChannelType, default: int = 0) -> int:
        """Get the number of channels for a specific type."""
        if key not in get_args(ModbusChannelType):
            raise ValueError(f"Invalid channel type: {key}")
        return self._spec.get(key, default)

    def __getattr__(self, key: str) -> int:
        """Get the number of channels for a specific type."""
        # Only handle valid ModbusChannelType keys
        if key in get_args(ModbusChannelType):
            return self._spec.get(cast(ModbusChannelType, key), 0)
        # For everything else, raise AttributeError (let Python handle private/internal attributes)
        raise AttributeError(f"{self.__class__.__name__!r} object has no attribute {key!r}")

    def __setattr__(self, key: str, value: int) -> None:
        """Set the number of channels for a specific type."""
        if key in get_args(ModbusChannelType):
            self._spec[cast(ModbusChannelType, key)] = value
        else:
            super().__setattr__(key, value)

    def __delattr__(self, key: str) -> None:
        """Delete the number of channels for a specific type."""
        if key in get_args(ModbusChannelType):
            del self._spec[cast(ModbusChannelType, key)]
        else:
            super().__delattr__(key)

    def __repr__(self) -> str:
        """Get the string representation of the ModbusChannelSpec."""
        return f"ModbusChannelSpec({self._spec})"

    def __str__(self) -> str:
        """Get the string representation of the ModbusChannelSpec."""
        return f"ModbusChannelSpec({self._spec})"

    def __contains__(self, key: ModbusChannelType) -> bool:
        """Check if the ModbusChannelSpec contains a specific type."""
        if key not in get_args(ModbusChannelType):
            raise ValueError(f"Invalid channel type: {key}")
        return key in self._spec

    def channel_count(self, key: ModbusChannelType | None = None) -> int:
        """Get the number of channels for a specific type."""
        if key is None:
            return sum(self._spec.values())
        if key not in get_args(ModbusChannelType):
            raise ValueError(f"Invalid channel type: {key}")
        return self._spec[key]

    def items(self) -> ItemsView[ModbusChannelType, int]:
        """Get the items of the ModbusChannelSpec."""
        return self._spec.items()


def auto_reconnect(func: Callable, retries: int = 3) -> Callable:
    """Annotate the function to automatically reconnect to the Modbus server."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(retries):
            try:
                return func(*args, **kwargs)
            except BrokenPipeError as e:  # noqa: PERF203
                log.warning(
                    "Failed to execute %s: %s, reconnecting...", func.__name__, e
                )
                args[0].reconnect()
        raise ModbusCommunicationError(
            f"Failed to execute {func.__name__} after {retries} retries"
        )

    return wrapper


class ModbusState:
    """Class for handling the state of a Modbus connection."""

    def __init__(
        self,
        state_width: ModbusChannelSpec | None = None,
        state: Self | dict[ModbusChannelType, int | Bits | Words] | None = None,
    ) -> None:
        """Initialize the ModbusState.

        Args:
            state_width: The width of the state.
            state: The state to initialize the ModbusState with.

        """
        if state_width is not None:
            self.coil: Bits = Bits(size=state_width.coil)
            self.discrete: Bits = Bits(size=state_width.discrete)
            self.input: Words = Words(size=state_width.input)
            self.holding: Words = Words(size=state_width.holding)
        elif state is not None:
            if isinstance(state, ModbusState):
                self.coil = state.coil.copy()
                self.discrete = state.discrete.copy()
                self.input = state.input.copy()
                self.holding = state.holding.copy()
            else:
                if not isinstance(state["coil"], Bits):
                    raise TypeError("coil must be a Bits object")
                if not isinstance(state["discrete"], Bits):
                    raise TypeError("discrete must be a Bits object")
                if not isinstance(state["input"], Words):
                    raise TypeError("input must be a Words object")
                if not isinstance(state["holding"], Words):
                    raise TypeError("holding must be a Words object")

                self.coil = (
                    state["coil"]
                    if isinstance(state["coil"], Bits)
                    else Bits(size=state["coil"])
                )
                self.discrete = (
                    state["discrete"]
                    if isinstance(state["discrete"], Bits)
                    else Bits(size=state["discrete"])
                )
                self.input = (
                    state["input"]
                    if isinstance(state["input"], Words)
                    else Words(size=state["input"])
                )
                self.holding = (
                    state["holding"]
                    if isinstance(state["holding"], Words)
                    else Words(size=state["holding"])
                )
        else:
            raise ValueError("Either state_width or state must be provided")

    def __getitem__(self, key: ModbusChannelType) -> Words | Bits:
        """Get the state of a specific channel type."""
        return getattr(self, key)

    def __setitem__(self, key: ModbusChannelType, value: Words | Bits) -> None:
        """Set the state of a specific channel type."""
        setattr(self, key, value)

    def __len__(self) -> int:
        """Get the total number of channels in the ModbusState."""
        return len(self.coil) + len(self.discrete) + len(self.input) + len(self.holding)

    def copy(self) -> "ModbusState":
        """Create a copy of the ModbusState."""
        new_state = ModbusState.__new__(ModbusState)
        new_state.coil = self.coil.copy()
        new_state.discrete = self.discrete.copy()
        new_state.input = self.input.copy()
        new_state.holding = self.holding.copy()
        return new_state

    def get_changed_addresses(
        self, other: Self, channel_types: Optional[list[ModbusChannelType]] = None
    ) -> dict[ModbusChannelType, set[int]]:
        """Get the addresses that have changed between the current state and the previous state."""
        changed_addresses: dict[ModbusChannelType, set[int]] = {}
        if channel_types is None:
            channel_types = list(get_args(ModbusChannelType))
        for key in channel_types or []:
            changed_addresses[key] = set()
            self_state = getattr(self, key)
            other_state = getattr(other, key)
            # Get the minimum length to avoid index errors
            min_length = min(len(self_state), len(other_state))

            # Compare values at each address in the range
            for i in range(min_length):
                if self_state[i] != other_state[i]:
                    changed_addresses[key].add(i)

            # If one state is longer than the other, all the additional addresses have changed
            if len(self_state) > min_length:
                changed_addresses[key].update(range(min_length, len(self_state)))
            if len(other_state) > min_length:
                changed_addresses[key].update(range(min_length, len(other_state)))

        return changed_addresses


class ModbusConnection:
    """Class for representing the Modbus connection to a Wago 750 hub.

    Used to update and cache the state of the modules connected to the hub.

    Args:
        modbus_tcp_client: The Modbus TCP client to use for the connection.
        count_bits_analog_in: The number of bits in the analog input registers.
        count_bits_analog_out: The number of bits in the analog output registers.
        count_bits_digital_in: The number of bits in the digital input registers.
        count_bits_digital_out: The number of bits in the digital output registers.

    Properties:
        state: The state of the Modbus connection.

    """

    def __init__(
        self,
        modbus_tcp_client: ModbusTcpClient,
        bits_in_state: ModbusChannelSpec,
        update_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the ModbusConnection.

        Args:
            modbus_tcp_client: The Modbus TCP client to use for communication.
            bits_in_state: Dictionary specifying the number of bits for each channel type.
            update_interval: The interval in milliseconds between updates.

        """
        self.modbus_tcp_client = modbus_tcp_client
        self.bits_in_state: ModbusChannelSpec = bits_in_state
        self.state: ModbusState = ModbusState(
            ModbusChannelSpec(
                input=self.bits_in_state.input // 16,
                holding=self.bits_in_state.holding // 16,
                discrete=self.bits_in_state.discrete,
                coil=self.bits_in_state.coil,
            )
        )
        self._update_thread: Thread | None = None
        self._running = False
        # Default update intervals in seconds for each state type
        self._update_intervals = {
            "input": update_interval,
            "holding": update_interval,
            "discrete": update_interval,
            "coil": update_interval,
        }
        self._last_updates = {
            "input": 0.0,
            "holding": 0.0,
            "discrete": 0.0,
            "coil": 0.0,
        }

        # Channel callback registry: {channel_type: {address: [channels]}}
        self._channel_registry: dict[
            ModbusChannelType, dict[int, list[Any]]
        ] = {
            "input": {},
            "holding": {},
            "discrete": {},
            "coil": {},
        }

    def reconnect(self) -> None:
        """Reconnect to the Modbus server."""
        if not self.modbus_tcp_client.is_socket_open():
            self.modbus_tcp_client.connect()
        else:
            self.modbus_tcp_client.close()
            self.modbus_tcp_client.connect()

    @auto_reconnect
    def _update_input_state(
        self, address: Optional[int] = None, width: Optional[int] = None
    ) -> None:
        """Update the state of the input registers.

        Args:
            address: The address of the first input register to update. Start address to read from.
            width: The number of input registers to update. Default is the entire input state.

        """
        if address is None:
            address = 0x0000
        if width is None:
            width = (
                self.bits_in_state["input"] // 16 - address
            )  # if no width is provided, read the entire input state starting from the address
        registers = Words(
            self.modbus_tcp_client.read_input_registers(address, count=width).registers
        )
        log.debug(
            "Updating input state from 0x%s - 0x%s with width %d",
            f"{address:04x}",
            f"{address + width:04x}",
            width,
        )
        log.debug("Registers: %s", registers.value_to_hex())
        self.state.input[address : address + width] = registers

    @auto_reconnect
    def _update_holding_state(
        self, address: Optional[int] = None, width: Optional[int] = None
    ) -> None:
        """Update the state of the holding registers.

        Args:
            address: The address of the first holding register to update.
            width: The number of holding registers to update.

        """
        if address is None:
            address = 0x0200
        else:
            address = address + 0x0200
        if width is None:
            width = (self.bits_in_state["holding"] // 16 + 0x0200) - address
        registers = Words(
            self.modbus_tcp_client.read_holding_registers(
                address, count=width
            ).registers
        )
        log.debug(
            "Updating holding state from 0x%s - 0x%s with width %d",
            f"{address:04x}",
            f"{address + width:04x}",
            width,
        )
        log.debug("Registers: %s", registers.value_to_hex())
        self.state.holding[address - 0x0200 : address + width - 0x0200] = registers

    @auto_reconnect
    def _update_discrete_state(
        self, address: Optional[int] = None, width: Optional[int] = None
    ) -> None:
        """Update the state of the discrete inputs.

        Args:
            address: The address of the first discrete input to update.
            width: The number of discrete inputs to update.

        """
        if address is None:
            address = 0x0000
        else:
            address = address + 0x0000
        if width is None:
            width = (self.bits_in_state["discrete"] + 0x0000) - address
        bits = Bits(
            self.modbus_tcp_client.read_discrete_inputs(address, count=width).bits,
            size=width,
        )
        log.debug(
            "Updating discrete state from 0x%s - 0x%s with width %d",
            f"{address:04x}",
            f"{address + width:04x}",
            width,
        )
        log.debug("Bits: %s", bits.value_to_bin())
        self.state.discrete[address : address + width] = bits

    @auto_reconnect
    def _update_coil_state(
        self, address: Optional[int] = None, width: Optional[int] = None
    ) -> None:
        """Update the state of the coils.

        Args:
            address: The address of the first coil to update.
            width: The number of coils to update.

        """
        if address is None:
            address = 0x0200
        else:
            address = address + 0x0200
        if width is None:
            width = (self.bits_in_state["coil"] + 0x0200) - address
        bits = Bits(
            self.modbus_tcp_client.read_coils(address, count=width).bits, size=width
        )
        log.debug(
            "Updating coil state from 0x%s - 0x%s with width %d",
            f"{address:04x}",
            f"{address + width:04x}",
            width,
        )
        log.debug("Bits: %s", bits.value_to_bin())
        self.state.coil[address - 0x0200 : address + width - 0x0200] = bits

    def update_state(
        self,
        states_to_update: list[ModbusChannelType] | ModbusChannelType | None = None,
    ) -> None:
        """Update the state of the ModbusConnection."""
        if states_to_update is None:
            states_to_update = ["coil", "discrete", "input", "holding"]
        if isinstance(states_to_update, str):
            states_to_update = [states_to_update]

        current_state = self.state.copy()
        for modbus_channel_type in states_to_update:
            # Store the current state before updating

            # Update the state
            if modbus_channel_type == "input":
                self._update_input_state()
            elif modbus_channel_type == "holding":
                self._update_holding_state()
            elif modbus_channel_type == "discrete":
                self._update_discrete_state()
            elif modbus_channel_type == "coil":
                self._update_coil_state()

            # Get changed addresses
            changed_addresses = self.state.get_changed_addresses(
                current_state, channel_types=[modbus_channel_type]
            )

            # Notify channels about changes
            self._notify_channels_of_changes(
                modbus_channel_type, changed_addresses[modbus_channel_type]
            )

    def _notify_channels_of_changes(
        self, channel_type: ModbusChannelType, changed_addresses: set[int]
    ) -> None:
        """Notify registered channels about changes in their addresses."""
        for address in changed_addresses:
            if address in self._channel_registry[channel_type]:
                for channel in self._channel_registry[channel_type][address]:
                    # Read the new value and notify the channel
                    if channel_type == "input":
                        value = self.read_input_register(address)
                    elif channel_type == "holding":
                        value = self.read_holding_register(address)
                    elif channel_type == "discrete":
                        value = self.read_discrete_input(address)
                    elif channel_type == "coil":
                        value = self.read_coil(address)
                    else:
                        continue

                    # check if the object has a notify_value_change method
                    if hasattr(channel, "notify_value_change"):
                        channel.notify_value_change(value)

    def _continuous_update(self) -> None:
        """Continuously update the state of the Modbus connection in a separate thread.

        Each state type (input, holding, discrete, coil) is updated according to
        its own interval.
        """
        if not self._running:
            log.info("Starting continuous state update thread")
            self._running = True

        update_counter = dict.fromkeys(self._update_intervals, 0)
        last_log_time = time.time()
        while self._running:
            try:
                current_time = time.time()
                # Check and update each state type based on its interval
                for state_type, interval in self._update_intervals.items():
                    if current_time - self._last_updates[state_type] >= interval / 1000:
                        log.debug("Updating %s state", state_type)
                        update_counter[state_type] += 1
                        self.update_state(cast(ModbusChannelType, state_type))
                        self._last_updates[state_type] = current_time
                if current_time - last_log_time > 30:
                    log.info("Updates in last 30 seconds: %s", str(update_counter))
                    update_counter = dict.fromkeys(self._update_intervals, 0)
                    last_log_time = current_time

                # Sleep for a short time to prevent excessive CPU usage
                # Use the smallest interval as the sleep time, but minimum 0.01 second
                min_interval = min(self._update_intervals.values())
                time.sleep(min(min_interval / 1000, 0.01))

            except Exception as e:  # pylint: disable=broad-exception-caught # noqa: PERF203 BLE001
                # TODO: Dont catch broad exception
                log.error("Error in continuous update thread: %s", e)
                time.sleep(0.5)  # Pause briefly after an error

    def start_continuous_update(
        self,
        interval: int | None = None,
        input_interval: int | None = None,
        holding_interval: int | None = None,
        discrete_interval: int | None = None,
        coil_interval: int | None = None,
    ) -> None:
        """Start the continuous update of the state."""
        self.set_update_interval(
            interval, input_interval, holding_interval, discrete_interval, coil_interval
        )

        if not self._running:
            self._running = True
            self._update_thread = Thread(target=self._continuous_update, daemon=True)
            self._update_thread.start()

    def set_update_interval(
        self,
        interval: int | None = None,
        input_interval: int | None = None,
        holding_interval: int | None = None,
        discrete_interval: int | None = None,
        coil_interval: int | None = None,
    ) -> None:
        """Set the update interval for the continuous update thread.

        Args:
            interval: Time in milliseconds between updates for all state types.
            input_interval: Time in milliseconds between input register updates.
            holding_interval: Time in milliseconds between holding register updates.
            discrete_interval: Time in milliseconds between discrete input updates.
            coil_interval: Time in milliseconds between coil updates.

        """
        # Set individual intervals if provided
        if interval is not None:
            # If a general interval is provided, use it for all state types
            for state_type in self._update_intervals:
                self._update_intervals[state_type] = interval
            log.info(
                "Setting update interval for all state types to %s seconds", interval
            )
        if input_interval is not None:
            self._update_intervals["input"] = input_interval
            log.info(
                "Setting input state update interval to %s seconds", input_interval
            )

        if holding_interval is not None:
            self._update_intervals["holding"] = holding_interval
            log.info(
                "Setting holding state update interval to %s seconds",
                holding_interval,
            )

        if discrete_interval is not None:
            self._update_intervals["discrete"] = discrete_interval
            log.info(
                "Setting discrete state update interval to %s seconds",
                discrete_interval,
            )

        if coil_interval is not None:
            self._update_intervals["coil"] = coil_interval
            log.info("Setting coil state update interval to %s seconds", coil_interval)

    def stop_continuous_update(self) -> None:
        """Stop the continuous update thread."""
        if self._update_thread is None or not self._update_thread.is_alive():
            log.warning("No continuous update thread running")
            return

        log.info("Stopping continuous update thread")
        self._running = False
        self._update_thread.join(
            timeout=2 * min(self._update_intervals.values()) / 1000
        )
        if self._update_thread.is_alive():
            log.warning("Continuous update thread did not terminate gracefully")
        self._update_thread = None

    def read_input_register(self, address: int, update: bool = False) -> int:
        """Read a single input register at the specified address."""
        if update:
            self._update_input_state(address, 1)

        register_value = self.state["input"][address]
        if isinstance(register_value, (Words, Bits)):
            return register_value.value_to_int()
        return register_value

    def read_input_registers(
        self, address: int, width: int, update: bool = False
    ) -> Words:
        """Read multiple input registers starting at the specified address."""
        if update:
            self._update_input_state(address, width)

        registers = self.state["input"][address : address + width]
        if isinstance(registers, Words):
            return registers
        if isinstance(registers, Bits):
            # Convert to Words if necessary
            return Words([registers.value_to_int()])
        return Words([registers])

    def read_holding_register(self, address: int, update: bool = False) -> int:
        """Read a single holding register at the specified address."""
        if update:
            self._update_holding_state(address, 1)

        register_value = self.state["holding"][address]
        if isinstance(register_value, (Words, Bits)):
            return register_value.value_to_int()
        return register_value

    def read_holding_registers(
        self, address: int, width: int, update: bool = False
    ) -> Words:
        """Read multiple holding registers starting at the specified address."""
        if update:
            self._update_holding_state(address, width)

        registers = self.state.holding[address : address + width]
        if isinstance(registers, Words):
            return registers
        if isinstance(registers, Bits):
            # Convert to Words if necessary
            return Words([registers.value_to_int()])
        return Words([registers])

    def read_discrete_input(self, address: int, update: bool = False) -> bool:
        """Read a discrete input at the specified address."""
        if update:
            self._update_discrete_state(address, 1)

        input_value = self.state.discrete[address]
        if isinstance(input_value, Bits):
            return bool(input_value.value_to_int())
        return bool(input_value)

    def read_discrete_inputs(
        self, address: int, width: int, update: bool = False
    ) -> Bits:
        """Read the values of a range of discrete inputs.

        Args:
            address: The address of the first discrete input to read.
            width: The number of discrete inputs to read.
            update: Whether to update the state of the discrete inputs.

        """
        if update:
            log.debug("Updating discrete state from modbus")
            self._update_discrete_state(address, width)
        value = Bits(self.state.discrete[address : address + width])
        log.debug(
            "Reading discrete inputs from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + width:04x}",
            value.value_to_bin(),
        )
        return value

    def read_coil(self, address: int, update: bool = False) -> bool:
        """Read a coil at the specified address."""
        if update:
            self._update_coil_state(address, 1)

        coil_value = self.state["coil"][address]
        if isinstance(coil_value, Bits):
            return bool(coil_value.value_to_int())
        return bool(coil_value)

    def read_coils(self, address: int, width: int, update: bool = False) -> Bits:
        """Read the values of a range of coils.

        Args:
            address: The address of the first coil to read.
            width: The number of coils to read.
            update: Whether to update the state before reading.

        """
        if update:
            self._update_coil_state(address, width)
        value = Bits(self.state.coil[address : address + width])
        log.debug(
            "Reading coils from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + width:04x}",
            value.value_to_bin(),
        )
        return value

    @auto_reconnect
    def write_coil(self, address: int, value: bool) -> None:
        """Set the state of a single coil.

        Args:
            address: The address of the coil to set.
            value: The value to set the coil to.

        """
        log.debug("Writing coil 0x%s Value: %s", f"{address:04x}", value)
        self.modbus_tcp_client.write_coil(address, value)
        self._update_coil_state()

    @auto_reconnect
    def write_coils(self, address: int, bits: Bits) -> None:
        """Set the state of a range of coils.

        Args:
            address: The address of the first coil to set.
            bits: The values to set the coils to.

        """
        log.debug(
            "Writing coils from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + len(bits):04x}",
            bits.value_to_bin(),
        )
        self.modbus_tcp_client.write_coils(address, bits.value.tolist())
        self._update_coil_state()

    @auto_reconnect
    def write_register(self, address: int, value: int) -> None:
        """Write a value to a single 16-bit register.

        Args:
            address: The address of the register to set.
            value: The value to set the register to.

        """
        log.debug(
            "Writing register 0x%s Value: 0x%s (%s)",
            f"{address:04x}",
            f"{value:04x}",
            f"0b{value:016b}",
        )
        self.modbus_tcp_client.write_register(address, value)
        self._update_holding_state()

    @auto_reconnect
    def write_registers(self, address: int, registers: Words) -> None:
        """Write a value to a range of 16-bit registers.

        Args:
            address: The address of the first register to set.
            registers: The values to set the registers to.

        """
        log.debug(
            "Writing registers from 0x%s - 0x%s Value: %s (%s)",
            f"{address:04x}",
            f"{address + len(registers):04x}",
            registers.value_to_hex(),
            registers.value_to_bin(),
        )
        self.modbus_tcp_client.write_registers(address, registers.value.tolist())
        self._update_holding_state()

    def register_channel_callback(
        self, modbus_channel: "ModbusChannel", object: object
    ) -> None:
        """Register a callback to be called when a channel value changes."""
        if modbus_channel.channel_type not in self._channel_registry:
            log.warning(
                "Cannot register callback for unsupported channel type: %s",
                modbus_channel.channel_type,
            )
            return

        if (
            modbus_channel.address
            not in self._channel_registry[modbus_channel.channel_type]
        ):
            self._channel_registry[modbus_channel.channel_type][
                modbus_channel.address
            ] = []

        self._channel_registry[modbus_channel.channel_type][
            modbus_channel.address
        ].append(object)

    def unregister_channel_callback(
        self, modbus_channel: "ModbusChannel", object: Any
    ) -> None:
        """Unregister a callback for a channel."""
        if (
            modbus_channel.channel_type in self._channel_registry
            and modbus_channel.address
            in self._channel_registry[modbus_channel.channel_type]
        ):
            channel_list = self._channel_registry[modbus_channel.channel_type][
                modbus_channel.address
            ]
            if object in channel_list:
                channel_list.remove(object)


class ModbusChannel:
    """Base Class for Modbus Channel representation.

    All Modbus Channel types inherit from this class.
    """

    channel_type: ClassVar[ModbusChannelType | None] = None

    def __init__(self, address: int, modbus_connection: ModbusConnection) -> None:
        """Initialize the Modbus Channel.

        Args:
            address: The address of the channel.
            modbus_connection: The modbus connection to use.

        """
        self.address = address
        self.modbus_connection = modbus_connection
        self.state: ModbusChannelState | None = None
        if self.channel_type is None:
            raise ValueError(f"Channel type not set in {self.__class__.__name__}")

    def __repr__(self) -> str:
        """Get a representation of the channel."""
        return f"{self.__class__.__name__} object with id {hex(id(self))} (address={self.address}, channel_type={self.channel_type})"

    @abstractmethod
    def read(self, update: bool = False) -> int | bool:
        """Read the state of the channel.

        Args:
            update: Whether to read the state of the channel from the modbus connection.

        Returns:
            The state of the channel. Must be implemented by a subclass.

        """
        raise NotImplementedError

    @abstractmethod
    def write(self, value: Any) -> None:  # pylint: disable=unused-argument
        """Update the state of the channel.

        Args:
            value: The value to write to the channel.

        """
        if self.channel_type not in ["coil", "holding"]:
            raise TypeError("This channel does not support writing")

        raise NotImplementedError

    def read_lsb(self, update: bool = False) -> int:
        """Read the least significant byte of the channel."""
        raise TypeError(
            "This channel does not support reading the least significant byte"
        )

    def read_msb(self, update: bool = False) -> int:
        """Read the most significant byte of the channel."""
        raise TypeError(
            "This channel does not support reading the most significant byte"
        )

    def write_lsb(self, value: int) -> None:
        """Write the least significant byte of the channel."""
        raise TypeError(
            "This channel does not support reading the most significant byte"
        )

    def write_msb(self, value: int) -> None:
        """Write the most significant byte of the channel."""
        raise TypeError(
            "This channel does not support writing the most significant byte"
        )

    @classmethod
    def create(
        cls,
        modbus_channel_type: ModbusChannelType,
        address: AddressDict,
        modbus_connection: ModbusConnection,
    ) -> Self:
        """Create a subclass of the given type.

        Args:
            modbus_channel_type: The type of the channel to get the subclass for.
            address: The address of the channel to create.
            modbus_connection: The modbus connection to use.

        """
        for subclass in cls.__subclasses__():
            if subclass.channel_type == modbus_channel_type:
                return subclass(
                    address=address.get(modbus_channel_type, 0),
                    modbus_connection=modbus_connection,
                )
        raise ValueError(
            f"Class for type {modbus_channel_type} not found in {cls.__name__}"
        )

    @classmethod
    def create_channels(
        cls,
        count: ModbusChannelSpec,
        address: AddressDict,
        modbus_connection: ModbusConnection,
    ) -> dict[ModbusChannelType, list[Self]]:
        """Create a list of channels of the given type.

        Args:
            count: The number of channels to create.
            address: The address of the first channel to create.
            modbus_connection: The modbus connection to use.

        """
        return {
            module_type: [
                cls.create(
                    module_type,
                    {k: v + i for k, v in address.items()},
                    modbus_connection,
                )
                for i in range(count)
            ]
            for module_type, count in count.items()
        }


class Coil(ModbusChannel):
    """Class for representing a Modbus coil."""

    channel_type: ClassVar[ModbusChannelType] = "coil"

    def read(self, update: bool = False) -> bool:
        """Read the state of the coil."""
        log.debug("Reading coil at address 0x%s", f"{self.address:04x}")
        return self.modbus_connection.read_coil(self.address, update)

    def write(self, value: bool) -> None:
        """Write the state of the coil."""
        log.debug(
            "Writing coil at address 0x%s Value: %s", f"{self.address:04x}", value
        )
        self.modbus_connection.write_coil(self.address, value)


class Discrete(ModbusChannel):
    """Class for representing a Modbus discrete input."""

    channel_type: ClassVar[ModbusChannelType] = "discrete"

    def read(self, update: bool = False) -> bool:
        """Read the state of the discrete input."""
        log.debug("Reading discrete input at address 0x%s", f"{self.address:04x}")
        return self.modbus_connection.read_discrete_input(self.address, update)

    def write(self, value: bool) -> None:
        """Write the state of the discrete input."""
        raise ValueError("Can not write to discrete channel")


class Holding(ModbusChannel):
    """Class for representing a Modbus holding register."""

    channel_type: ClassVar[ModbusChannelType] = "holding"

    def read(self, update: bool = False) -> int:
        """Read the state of the holding register."""
        log.debug("Reading holding register at address 0x%s", f"{self.address:04x}")
        return self.modbus_connection.read_holding_register(self.address, update)

    def read_lsb(self, update: bool = False) -> int:
        """Read the least significant byte of the input register."""
        log.debug(
            "Reading LSB of holding register at address 0x%s", f"{self.address:04x}"
        )
        return (
            int(self.modbus_connection.read_holding_register(self.address, update))
            & 0xFF
        )

    def read_msb(self, update: bool = False) -> int:
        """Read the most significant byte of the input register."""
        log.debug(
            "Reading MSB of holding register at address 0x%s", f"{self.address:04x}"
        )
        return (
            int(self.modbus_connection.read_holding_register(self.address, update))
            & 0xFF00
        ) >> 8

    def write(self, value: int) -> None:
        """Write the state of the holding register."""
        log.debug(
            "Writing holding register at address 0x%s Value: 0x%s(%s)",
            f"{self.address:04x}",
            f"{value:04x}",
            f"0b{value:016b}",
        )
        self.modbus_connection.write_registers(self.address, Words([value]))

    def write_lsb(self, value: int) -> None:
        """Write the least significant byte of the holding register."""
        log.debug(
            "Writing LSB of holding register at address 0x%s Value: 0x%s(%s)",
            f"{self.address:04x}",
            f"{value:02x}",
            f"0b{value:08b}",
        )
        msb = int(self.read_msb(update=True))
        self.modbus_connection.write_registers(
            self.address, Words([(msb << 8) | value])
        )

    def write_msb(self, value: int) -> None:
        """Write the most significant byte of the holding register."""
        lsb = int(self.read_lsb(update=True))
        log.debug(
            "Writing MSB of holding register at address 0x%s Value: 0x%s(%s)",
            f"{self.address:04x}",
            f"{value:02x}",
            f"0b{value:08b}",
        )
        self.modbus_connection.write_registers(
            self.address, Words([(value << 8) | lsb])
        )


class Input(ModbusChannel):
    """Class for representing a Modbus input register."""

    channel_type: ClassVar[ModbusChannelType] = "input"

    def read(self, update: bool = False) -> int:
        """Read the state of the input register."""
        log.debug("Reading input register at address 0x%s", f"{self.address:04x}")
        return self.modbus_connection.read_input_register(self.address, update)

    def write(self, value: int) -> None:
        """Write a value to the input register."""
        log.debug(
            "Writing input register at address 0x%s Value: 0x%s(%s)",
            f"{self.address:04x}",
            f"{value:04x}",
            f"0b{value:016b}",
        )
        raise ValueError("Can not write to input channel")

    def read_lsb(self, update: bool = False) -> int:
        """Read the least significant byte of the input register."""
        log.debug(
            "Reading LSB of input register at address 0x%s", f"{self.address:04x}"
        )
        return (
            int(self.modbus_connection.read_input_register(self.address, update)) & 0xFF
        )

    def read_msb(self, update: bool = False) -> int:
        """Read the most significant byte of the input register."""
        log.debug(
            "Reading MSB of input register at address 0x%s", f"{self.address:04x}"
        )
        return (
            int(self.modbus_connection.read_input_register(self.address, update))
            & 0xFF00
        ) >> 8
