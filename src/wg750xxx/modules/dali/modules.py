"""Dali module."""

from collections.abc import Callable, Iterator
from logging import getLogger
from typing import Any, ClassVar, cast

from wg750xxx.modules.exceptions import WagoModuleError
from wg750xxx.modules.module import WagoModule
from wg750xxx.modules.spec import IOType, ModbusChannelSpec, ModuleSpec

from .channels import DaliChannel
from .dali_communication import DaliCommunicationRegister
from .exceptions import DaliError
from .module_commands import ModuleCommands
from .module_setup import ModuleSetup
from .module_status import ModuleStatus

_LOGGER = getLogger(__name__)


class Wg750DaliMaster(WagoModule):
    """750-641 1-Kanal DALI Master."""

    description: str = "750-641 1-Kanal DALI Master"
    aliases: ClassVar[list[str]] = ["641"]
    display_name: ClassVar[str] = "Dali"
    spec: ModuleSpec = ModuleSpec(
        io_type=IOType(input=True, output=True),
        modbus_channels=ModbusChannelSpec(input=3, holding=3),
    )
    _initialized: bool = False

    # @overrides(MySuperInterface)
    def __init__(self, *args, **kwargs) -> None:
        """Initialize the DALI master.

        Args:
            *args: The arguments to pass to the superclass.
            **kwargs: The keyword arguments to pass to the superclass.

        """
        super().__init__(*args, **kwargs)
        if self.modbus_address is None:
            raise WagoModuleError("Modbus address not set")
        self.dali_communication_register: DaliCommunicationRegister = (
            DaliCommunicationRegister(self.modbus_connection, self.modbus_address)
        )
        # self.dali_communication_register.read()
        self._initialized = True
        if self.auto_create_channels:
            self.create_channels()
            self.groups: list[DaliChannel] = [
                DaliChannel(address, self.dali_communication_register)
                for address in range(0x40, 0x50)
            ]
            self.all: DaliChannel = DaliChannel(0x3F, self.dali_communication_register)

        self.setup: ModuleSetup = ModuleSetup(self.dali_communication_register)
        self.status: ModuleStatus = ModuleStatus(self.dali_communication_register)
        self.commands: ModuleCommands = ModuleCommands(self.dali_communication_register)

    def __getitem__(self, key: int) -> DaliChannel | None:
        """Get a DALI channel by index."""
        if self.channels is None:
            return None
        channel = self.channels[key]
        if isinstance(channel, DaliChannel):
            return channel
        return None

    def __len__(self) -> int:
        """Get the number of DALI channels."""
        if self.channels is None:
            return 0
        return len(self.channels)

    def __iter__(self) -> Iterator[DaliChannel]:
        """Iterate over the DALI channels."""
        if self.channels is None:
            return iter([])
        return iter(cast(list[DaliChannel], self.channels))

    def create_channels(self) -> None:
        """Create the channels of the DALI master."""
        if not self._initialized:
            return
        module_setup = ModuleSetup(self.dali_communication_register)
        try:
            short_addresses = module_setup.query_short_address_present()
        except TimeoutError:
            _LOGGER.error(
                "Error setting up DALI channels: Timeout waiting for Dali Response"
            )
            return
        for dali_address in short_addresses:
            self.append_channel(
                DaliChannel(
                    dali_address=dali_address,
                    dali_communication_register=self.dali_communication_register,
                )
            )

    @property
    def on_change_callback(self) -> Callable[[Any, Any | None], None] | None:
        """Get the callback function that gets called when the channel value changes."""
        return self._on_change_callback

    @on_change_callback.setter
    def on_change_callback(
        self, callback: Callable[[Any, Any | None], None] | None
    ) -> None:
        """Set the callback function that gets called when the channel value changes."""
        self._on_change_callback = callback

        # If we have a modbus channel and a valid callback, register with ModbusConnection
        if len(self.modbus_channels["input"]) > 0 and callback is not None:
            if hasattr(self.modbus_connection, "register_channel_callback"):
                for channel in self.modbus_channels["input"]:
                    self.modbus_connection.register_channel_callback(channel, self)
        elif len(self.modbus_channels["input"]) > 0 and callback is None:
            # Unregister if callback is set to None
            if hasattr(self.modbus_connection, "unregister_channel_callback"):
                for channel in self.modbus_channels["input"]:
                    self.modbus_connection.unregister_channel_callback(channel, self)

    def notify_value_change(self, new_value: Any) -> None:
        """Notify the channel that its value has changed."""
        self.dali_communication_register.read_status_byte()
        self.dali_communication_register.read_control_byte()

        if (
            self.dali_communication_register.read_request()
        ):  # TODO: This is to find out why the DALI master is requesting a read.
            data = self.dali_communication_register.read()
            _LOGGER.warning(
                "DALI master is requesting an unexpected read before write: %s", data
            )
            raise DaliError("DALI master is requesting an unexpected read.")

        if not hasattr(self, "_on_change_callback") or self._on_change_callback is None:
            return

        code = getattr(self._on_change_callback, "__code__", None)
        if code is None or not hasattr(code, "co_argcount"):
            self._on_change_callback(new_value, self)
        elif code.co_argcount == 1:
            self._on_change_callback(new_value)
        elif code.co_argcount == 2:
            self._on_change_callback(new_value, self)
        else:
            raise ValueError(
                f"Callback function has {code.co_argcount} arguments, expected 1 or 2"
            )
