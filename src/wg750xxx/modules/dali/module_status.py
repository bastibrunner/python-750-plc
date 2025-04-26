"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
import logging

from .dali_communication import (
    DaliInputMessage,
    DaliOutputMessage,
)
from .misc import dali_response_to_channel_list
from .module_base import ModuleBase

log = logging.getLogger(__name__)


class ModuleStatus(ModuleBase):
    """DALI status."""

    # 8. Abfrage Status Vorschaltgerät [0-31]
    # 9. Abfrage Status Vorschaltgerät [32-63]
    def query_status_psu(self) -> list[int]:
        """Query status vorschaltgerät."""
        channels = []
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x08), response=True
                )
            )
        )
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x09), response=True
                )
            )
        )

    # 10. Abfrage Lampenausfall [0-31]
    # 11. Abfrage Lampenausfall [32-63]
    def query_lamp_failure(self) -> None:
        """Query lamp failure."""
        channels = []
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0A), response=True
                )
            )
        )
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0B), response=True
                )
            )
        )

    # 12. Abfrage Lampenleistung Ein [0-31]
    # 13. Abfrage Lampenleistung Ein [32-63]
    def query_lamp_power_on(self) -> list[int]:
        """Query lamp power on."""
        channels = []
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0C), response=True
                )
            )
        )
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0D), response=True
                )
            )
        )
        return channels

    # 19. Rückantworten auf QUERY ACTUAL LEVEL Geräte 56 bis 59
    def query_actual_level_device_56_to_59(self) -> None:
        """Query actual level device 56 to 59."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x13), response=True
        )

    # 20. Rückantworten auf QUERY ACTUAL LEVEL Geräte 60 bis 63
    def query_actual_level_device_60_to_63(self) -> None:
        """Query actual level device 60 to 63."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x14), response=True
        )

    # 23. Abfragen der Hard- und Softwareversion
    def query_hard_and_software_version(self) -> DaliInputMessage | None:
        """Query hard and software version."""
        return self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x17), response=True
        )

    # 36. Schnellabfragen des Netzwerk-Status
    def query_network_status(self) -> DaliInputMessage | None:
        """Query network status."""
        return self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x36), response=True
        )
