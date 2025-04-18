"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
import logging

from .dali_communication import (
    DaliCommunicationRegister,
    DaliInputMessage,
    DaliOutputMessage,
)
from .misc import iterate_bits

log = logging.getLogger(__name__)


class DaliCommands:
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

    # Macro Commands

    # 6. Query short address present [0-31]
    # 7. Query short address present [32-63]
    def query_short_address_present(self) -> list[int]:
        """Query short address present."""
        channels = []
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x06), response=True
                ),
                offset=0
            )
        )
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x07), response=True
                ),
                offset=32
            )
        )
        return channels

    # 8. Abfrage Status Vorschaltgerät [0-31]
    # 9. Abfrage Status Vorschaltgerät [32-63]
    def query_status_psu(self) -> None:
        """Query status vorschaltgerät."""
        channels = []
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x08), response=True
                )
            )
        )
        channels.extend(
            self._dali_response_to_channel_list(
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
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0A), response=True
                )
            )
        )
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0B), response=True
                )
            )
        )

    # 12. Abfrage Lampenleistung Ein [0-31]
    # 13. Abfrage Lampenleistung Ein [32-63]
    def query_lamp_power_on(self) -> None:
        """Query lamp power on."""
        channels = []
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0C), response=True
                )
            )
        )
        channels.extend(
            self._dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x0D), response=True
                )
            )
        )
        return channels

    # 14. Einstellung DALI/DSI-Modus und Polling
    def set_dali_dsi_mode_and_polling(self) -> None:
        """Set DALI/DSI mode and polling."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x0E, parameter_1=0x01)
        )

    # 15. Reset
    def reset(self) -> None:
        """Reset."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x0F)
        )

    # 16. Save scene value
    def save_scene_value(self, scene_value: int) -> None:
        """Save scene value."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x10, parameter_1=scene_value + 0x40)
        )

    # 17. Automatisches Pollen deaktivieren
    def disable_automatic_polling(self) -> None:
        """Disable automatic polling."""
        self.dali_communication_register.write(
            DaliOutputMessage(
                command_extension=0x11, parameter_1=0xFF, parameter_2=0xFF
            )
        )

    # 17. Automatisches Pollen aktivieren
    def enable_automatic_polling(self) -> None:
        """Enable automatic polling."""
        self.dali_communication_register.write(
            DaliOutputMessage(
                command_extension=0x11, parameter_1=0xE8, parameter_2=0x03
            )
        )

    # 18. Senden der Device Type spezifischen DALI-Befehle
    def send_device_type_specific_dali_commands(self) -> None:
        """Send device type specific DALI commands."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x12)
        )

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

    # 21. Abfragen der Level-Poll-Periode
    def set_level_poll_period(self, period: int) -> None:
        """Set level poll period."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x15, parameter_1=period), response=True
        )

    # 22. Setzen der Level-Poll-Periode
    def get_level_poll_period(self) -> None:
        """Get level poll period."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x16), response=True
        )

    # 23. Abfragen der Hard- und Softwareversion
    def query_hard_and_software_version(self) -> None:
        """Query hard and software version."""
        return self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x17), response=True
        )

    # 36. Schnellabfragen des Netzwerk-Status
    def query_network_status(self) -> None:
        """Query network status."""
        return self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x36), response=True
        )

    def _dali_response_to_channel_list(
        self, response: DaliInputMessage | None, offset: int = 0
    ) -> list[int]:
        """Convert DALI response to channel list."""
        channels = []
        if response is None:
            return channels
        channels.extend(
            [offset + i for bit, i in iterate_bits(response.dali_response) if bit]
        )
        channels.extend([offset + 8 + i for bit, i in iterate_bits(response.message_3) if bit])
        channels.extend([offset + 16 + i for bit, i in iterate_bits(response.message_2) if bit])
        channels.extend([offset + 24 + i for bit, i in iterate_bits(response.message_1) if bit])
        return channels
