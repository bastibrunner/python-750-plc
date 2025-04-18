"""Module for handling Modbus communication and channel types for WAGO 750 series I/O modules."""

from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
import logging
from threading import Thread
import time
from typing import Any, ClassVar, Literal, Self

from pymodbus.client import ModbusTcpClient

from .registers import Bits, Words
from .exceptions import ModbusException, ModbusConnectionError, ModbusTimeoutError, ModbusCommunicationError, ModbusProtocolError

log = logging.getLogger(__name__)
ModbusChannelType = Literal["coil", "discrete", "input", "holding"]
ModbusBits = list[bool]
AddressDict = dict[ModbusChannelType, int]
ModbusChannelState = int | bool
ModbusChannelSpec = dict[ModbusChannelType, int]
ModuleModbusState = dict[ModbusChannelType, Words | Bits]


def auto_reconnect(func: Callable, retries: int = 3) -> Callable:
    """Annotate the function to automatically reconnect to the Modbus server."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(retries):
            try:
                return func(*args, **kwargs)
            except BrokenPipeError as e:
                log.warning(
                    "Failed to execute %s: %s, reconnecting...", func.__name__, e
                )
                args[0].reconnect()
        raise ModbusCommunicationError(f"Failed to execute {func.__name__} after {retries} retries")

    return wrapper


@dataclass
class ModbusState:
    """Class for handling the state of a Modbus connection."""

    input_register_state: Words = Words([])
    holding_register_state: Words = Words([])
    discrete_input_state: Bits = Bits([])
    coil_state: Bits = Bits([])


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
        self, modbus_tcp_client: ModbusTcpClient, bits_in_state: ModbusChannelSpec
    ) -> None:
        """Initialize the ModbusConnection.

        Args:
            modbus_tcp_client: The Modbus TCP client to use for communication.
            bits_in_state: Dictionary specifying the number of bits for each channel type.

        """
        self.modbus_tcp_client = modbus_tcp_client
        self.bits_in_state = bits_in_state
        self.state: ModuleModbusState = ModuleModbusState(
            {
                "input": Words(size=self.bits_in_state["input"] // 16),
                "holding": Words(size=self.bits_in_state["holding"] // 16),
                "discrete": Bits(size=self.bits_in_state["discrete"]),
                "coil": Bits(size=self.bits_in_state["coil"]),
            }
        )
        self._update_thread = None
        self._running = False
        # Default update intervals in seconds for each state type
        self._update_intervals = {
            "input": 1.0,
            "holding": 1.0,
            "discrete": 1.0,
            "coil": 1.0,
        }
        self._last_updates = {
            "input": 0.0,
            "holding": 0.0,
            "discrete": 0.0,
            "coil": 0.0,
        }

    def reconnect(self) -> None:
        """Reconnect to the Modbus server."""
        if not self.modbus_tcp_client.is_socket_open():
            self.modbus_tcp_client.connect()
        else:
            self.modbus_tcp_client.close()
            self.modbus_tcp_client.connect()

    @auto_reconnect
    def update_input_state(
        self, address: int | None = None, width: int | None = None
    ) -> None:
        """Update the state of the input registers.

        Args:
            address: The address of the first input register to update. Start address to read from.
            width: The number of input registers to update. Default is the entire input state.

        """
        if address is None:
            address = 0x0000
        if width is None:
            width = self.bits_in_state["input"] // 16 - address  # if no width is provided, read the entire input state starting from the address
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
        self.state["input"][address : address + width] = registers.value

    @auto_reconnect
    def update_holding_state(
        self, address: int | None = None, width: int | None = None
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
        self.state["holding"][address - 0x0200 : address + width - 0x0200] = (
            registers.value
        )

    @auto_reconnect
    def update_discrete_state(
        self, address: int | None = None, width: int | None = None
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
        self.state["discrete"][address : address + width] = bits.value

    @auto_reconnect
    def update_coil_state(
        self, address: int | None = None, width: int | None = None
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
        self.state["coil"][address - 0x0200 : address + width - 0x0200] = bits.value

    def update_state(self) -> None:
        """Update the state of the Modbus connection."""
        self.update_input_state()
        self.update_holding_state()
        self.update_discrete_state()
        self.update_coil_state()

    def _continuous_update(self) -> None:
        """Continuously update the state of the Modbus connection in a separate thread.

        Each state type (input, holding, discrete, coil) is updated according to
        its own interval.
        """
        log.debug("Starting continuous state update thread")
        while self._running:
            try:
                current_time = time.time()

                # Check and update each state type based on its interval
                if (
                    current_time - self._last_updates["input"]
                    >= self._update_intervals["input"]
                ):
                    self.update_input_state()
                    self._last_updates["input"] = current_time

                if (
                    current_time - self._last_updates["holding"]
                    >= self._update_intervals["holding"]
                ):
                    self.update_holding_state()
                    self._last_updates["holding"] = current_time

                if (
                    current_time - self._last_updates["discrete"]
                    >= self._update_intervals["discrete"]
                ):
                    self.update_discrete_state()
                    self._last_updates["discrete"] = current_time

                if (
                    current_time - self._last_updates["coil"]
                    >= self._update_intervals["coil"]
                ):
                    self.update_coil_state()
                    self._last_updates["coil"] = current_time

                # Sleep for a short time to prevent excessive CPU usage
                # Use the smallest interval as the sleep time, but minimum 0.1 second
                min_interval = min(self._update_intervals.values())
                time.sleep(min(min_interval / 10, 0.1))

            except Exception as e:
                log.error("Error in continuous update thread: %s", e)
                time.sleep(0.5)  # Pause briefly after an error

    def start_continuous_update(
        self,
        interval: float = None,
        input_interval: float = None,
        holding_interval: float = None,
        discrete_interval: float = None,
        coil_interval: float = None,
    ) -> None:
        """Start a thread that continuously updates the Modbus state.

        Args:
            interval: Time in seconds between updates for all state types.
                     If specified, overrides all individual settings.
            input_interval: Time in seconds between input register updates.
            holding_interval: Time in seconds between holding register updates.
            discrete_interval: Time in seconds between discrete input updates.
            coil_interval: Time in seconds between coil updates.

        """
        if self._update_thread is not None and self._update_thread.is_alive():
            log.warning("Continuous update thread already running")
            return

        # Set individual intervals if provided
        if interval is not None:
            # If a general interval is provided, use it for all state types
            for state_type in self._update_intervals:
                self._update_intervals[state_type] = interval
            log.info(
                "Setting update interval for all state types to %s seconds", interval
            )
        else:
            # Otherwise, set individual intervals if provided
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
                log.info(
                    "Setting coil state update interval to %s seconds", coil_interval
                )

        # Initialize last update times to now
        current_time = time.time()
        for state_type in self._last_updates:
            self._last_updates[state_type] = current_time

        # Start the update thread
        self._running = True
        self._update_thread = Thread(target=self._continuous_update, daemon=True)
        self._update_thread.start()
        log.info(
            "Started continuous update thread with individual state type intervals"
        )

    def is_continuous_update_running(self) -> bool:
        """Check if the continuous update thread is running."""
        return self._running

    def stop_continuous_update(self) -> None:
        """Stop the continuous update thread."""
        if self._update_thread is None or not self._update_thread.is_alive():
            log.warning("No continuous update thread running")
            return

        log.info("Stopping continuous update thread")
        self._running = False
        self._update_thread.join(timeout=2 * min(self._update_intervals.values()))
        if self._update_thread.is_alive():
            log.warning("Continuous update thread did not terminate gracefully")
        self._update_thread = None

    def read_input_register(self, address: int, update: bool = False) -> int:
        """Read the value of a input register.

        Args:
            address: The address of the input register to read.
            update: Whether to update the state of the input register.

        """
        if update:
            self.update_input_state(address)
        value = self.state["input"][address]
        log.debug(
            "Reading input register 0x%s Value: %s",
            f"{address:04x}",
            value.value_to_int(),
        )
        return value.value_to_int()

    def read_input_registers(
        self, address: int, width: int, update: bool = False
    ) -> Words:
        """Read the values of a range of input registers.

        Args:
            address: The address of the first input register to read.
            width: The number of input registers to read.
            update: Whether to update the state of the input registers.

        """
        if update:
            self.update_input_state(address, width)
        value = self.state["input"][address : address + width]
        log.debug(
            "Reading input registers from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + width:04x}",
            value.value_to_hex(),
        )
        return value

    def read_holding_register(self, address: int, update: bool = False) -> int:
        """Read the value of a holding register.

        Args:
            address: The address of the holding register to read.
            update: Whether to update the state of the holding register.

        """
        if update:
            self.update_holding_state(address)
        value = self.state["holding"][address]
        log.debug(
            "Reading holding register 0x%s Value: %s",
            f"{address:04x}",
            value.value_to_int(),
        )
        return value.value_to_int()

    def read_holding_registers(
        self, address: int, width: int, update: bool = False
    ) -> Words:
        """Read the values of a range of holding registers.

        Args:
            address: The address of the first holding register to read.
            width: The number of holding registers to read.
            update: Whether to update the state of the holding registers.

        """
        if update:
            self.update_holding_state(address, width)
        value = self.state["holding"][address : address + width]
        log.debug(
            "Reading holding registers from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + width:04x}",
            value.value_to_hex(),
        )
        return value

    def read_discrete_input(self, address: int, update: bool = False) -> bool:
        """Read the value of a discrete input.

        Args:
            address: The address of the discrete input to read.
            update: Whether to update the state of the discrete input.

        """
        if update:
            self.update_discrete_state(address)
        value = self.state["discrete"][address]
        log.debug("Reading discrete input %d Value: %s", address, value)
        return bool(value)

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
            self.update_discrete_state(address, width)
        value = self.state["discrete"][address : address + width]
        log.debug(
            "Reading discrete inputs from 0x%s - 0x%s Value: %s",
            f"{address:04x}",
            f"{address + width:04x}",
            value.value_to_bin(),
        )
        return value

    def read_coil(self, address: int, update: bool = False) -> bool:
        """Read the value of a coil.

        Args:
            address: The address of the coil to read.
            update: Whether to update the state of the coil.

        """
        if update:
            self.update_coil_state(address)
        value = self.state["coil"][address]
        log.debug("Reading coil 0x%s Value: %s", f"{address:04x}", value)
        return bool(value)

    def read_coils(self, address: int, width: int, update: bool = False) -> Bits:
        """Read the values of a range of coils.

        Args:
            address: The address of the first coil to read.
            width: The number of coils to read.
            update: Whether to update the state before reading.

        """
        if update:
            self.update_coil_state(address, width)
        value = self.state["coil"][address : address + width]
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
        self.update_coil_state()

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
        self.modbus_tcp_client.write_coils(address, bits.value)
        self.update_coil_state()

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
        self.update_holding_state()

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
        self.modbus_tcp_client.write_registers(address, registers.value)
        self.update_holding_state()


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
