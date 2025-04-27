"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
from typing import Any

from ..exceptions import WagoModuleError
from .dali_communication import DaliCommunicationRegister, DaliOutputMessage


class DaliChannelBase:
    """DALI commands."""

    def __init__(
        self,
        dali_address: int,
        dali_communication_register: DaliCommunicationRegister,
        **kwargs: Any,
    ) -> None:
        """Initialize the DALI channel commands.

        Args:
            dali_address: int: The DALI address.
            dali_communication_register: DaliCommunicationRegister: The DALI communication register.
            **kwargs: Any: The keyword arguments.

        """
        self.dali_communication_register: DaliCommunicationRegister = (
            dali_communication_register
        )
        self._dali_address: int = dali_address
        super().__init__(**kwargs)

    @property
    def dali_address(self) -> int:
        """Get the DALI address."""
        return self._dali_address

    @dali_address.setter
    def dali_address(self, value: int) -> None:
        """Set the DALI address."""
        self._dali_address = value

    def _send_command(self, command_code: int, timeout: float = 5.0) -> None:
        """Write a command to the DALI channel."""
        self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address, command_code=command_code
            ),
            timeout=timeout,
        )

    def _send_config_command(self, command_code: int, timeout: float = 5.0) -> None:
        """Write a config command to the DALI channel (sending twice as expected by the DALI master)."""
        self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address, command_code=command_code
            ),
            timeout=timeout,
        )
        self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address, command_code=command_code
            ),
            timeout=timeout,
        )

    def _send_extended_command(
        self,
        command_extension: int,
        parameter_1: int | None = None,
        parameter_2: int | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Send an extended command."""
        self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address,
                command_extension=command_extension,
                parameter_1=parameter_1,
                parameter_2=parameter_2,
            ),
            timeout=timeout,
        )

    def _read_command(self, command_code: int) -> int:
        """Read a command from the DALI channel."""
        r = self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address, command_code=command_code
            ),
            response=True,
        )
        if r is None:
            raise WagoModuleError("Failed to get current value")
        return r.dali_response
