"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods

from .channel_base import DaliChannelBase
from .dali_communication import DaliOutputMessage
from .misc import check_value_range


class DaliChannelCommands(DaliChannelBase):
    """DALI commands."""

    # Dali Commands DIN IEC 60929

    # 0. Power off
    def power_off(self) -> None:
        """Power off."""
        self._send_command(0b00000000)

    # 1. Increase brightness
    def increase_brightness(self) -> None:
        """Increase brightness."""
        self._send_command(0b00000001)

    # 2. Decrease brightness
    def decrease_brightness(self) -> None:
        """Decrease brightness."""
        self._send_command(0b00000010)

    # 3. Increase brightness one step
    def increase_brightness_step(self) -> None:
        """Increase brightness one step."""
        self._send_command(0b00000011)

    # 4. Decrease brightness step
    def decrease_brightness_step(self) -> None:
        """Decrease brightness step."""
        self._send_command(0b00000100)

    # 7. Decrease brightness and power off
    def decrease_brightness_and_power_off(self) -> None:
        """Decrease brightness and power off."""
        self._send_command(0b00000111)

    # 8. Power on and increase brightness
    def power_on_and_increase_brightness(self) -> None:
        """Power on and increase brightness."""
        self._send_command(0b00001000)

    # 16-31. Go to scene
    def go_to_scene(self, scene: int) -> None:
        """Go to scene."""
        check_value_range(scene, 1, 16, "scene")
        self._send_command(0b00010000 + scene)

    # 160. Get current value
    def get_current_value(self) -> int:
        """Get current value."""
        r = self._read_command(0b10100000)
        return r

    # 999. WAGO specific: Direct brightness control
    def set_brightness(self, brightness: int) -> None:
        """Set brightness."""
        check_value_range(brightness, 0, 254, "brightness")
        self.dali_communication_register.write(
            DaliOutputMessage(dali_address=self.dali_address, brightness=brightness)
        )

    # Macro Commands
