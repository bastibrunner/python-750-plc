"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
import logging

from .dali_communication import DaliInputMessage, DaliOutputMessage
from .misc import dali_response_to_channel_list
from .module_base import ModuleBase

log = logging.getLogger(__name__)


class ModuleSetup(ModuleBase):
    """DALI commands."""

    # Macro Commands

    # 6. Query short address present [0-31]
    # 7. Query short address present [32-63]
    def query_short_address_present(self) -> list[int]:
        """Query short address present."""
        channels = []
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x06), response=True
                ),
                offset=0,
            )
        )
        channels.extend(
            dali_response_to_channel_list(
                self.dali_communication_register.write(
                    DaliOutputMessage(command_extension=0x07), response=True
                ),
                offset=32,
            )
        )
        return channels

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
        return channels

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

    # 21. Abfragen der Level-Poll-Periode
    @property
    def level_poll_period(self) -> DaliInputMessage | None:
        """Get level poll period."""
        return self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x16), response=True
        )

    @level_poll_period.setter
    def level_poll_period(self, period: int) -> None:
        """Set level poll period."""
        self.dali_communication_register.write(
            DaliOutputMessage(command_extension=0x15, parameter_1=period)
        )
