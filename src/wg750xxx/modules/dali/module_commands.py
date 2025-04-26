"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
import logging

from .dali_communication import (
    DaliCommunicationRegister,
    DaliOutputMessage,
)

log = logging.getLogger(__name__)


class ModuleCommands:
    """DALI commands."""

    def __init__(self, dali_communication_register: DaliCommunicationRegister) -> None:
        """Initialize the DALI commands.

        Args:
            dali_communication_register: DaliCommunicationRegister: The DALI communication register.

        """
        log.debug("Initializing DaliCommands %s", id(self))
        self.dali_communication_register: DaliCommunicationRegister = (
            dali_communication_register
        )
        self.dali_communication_register.read()

    # 18. Senden der Device Type spezifischen DALI-Befehle
    def send_device_type_specific_dali_commands(self) -> None:
        """Send device type specific DALI commands."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x12)
        )
