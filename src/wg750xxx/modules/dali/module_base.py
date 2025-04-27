"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
import logging

from .dali_communication import DaliCommunicationRegister

log = logging.getLogger(__name__)


class ModuleBase:
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
