"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods

from .channel_base import DaliChannelBase
from .dali_communication import DaliOutputMessage
from .misc import check_value_range, iterate_bits


class DaliChannelSetup(DaliChannelBase):
    """DALI commands."""

    # 5. Get current max value
    def get_current_max_value(self) -> int:
        """Get current max value."""
        self._send_command(0b00000101)
        return self.dali_communication_register.read().dali_response

    # 6. Get current min value
    def get_current_min_value(self) -> None:
        """Get current min value."""
        self._send_command(0b00000110)

    # 32. Reset
    def reset(self) -> None:
        """Reset."""
        self._send_config_command(0b00100000)

    # 33. Save current value to DTR
    def save_current_value_to_dtr(self) -> None:
        """Save current value to DTR."""
        self._send_config_command(0b00100001)

    # 42. Save DTR to max value
    def save_dtr_to_max_value(self) -> None:
        """Save DTR to max value."""
        self._send_config_command(0b00101010)

    # 43. Save DTR to min value
    def save_dtr_to_min_value(self) -> None:
        """Save DTR to min value."""
        self._send_config_command(0b00101011)

    # 44. Save DTR to system error value
    def save_dtr_to_system_error_value(self) -> None:
        """Save DTR to system error value."""
        self._send_config_command(0b00101100)

    # 45. Save DTR to power on value
    def save_dtr_to_power_on_value(self) -> None:
        """Save DTR to power on value."""
        self._send_config_command(0b00101101)

    # 46. Save DTR to step time
    def save_dtr_to_step_time(self) -> None:
        """Save DTR to step time."""
        self._send_config_command(0b00101110)

    # 47. Save DTR to step speed
    def save_dtr_to_step_speed(self) -> None:
        """Save DTR to step speed."""
        self._send_config_command(0b00101111)

    # 64-79. Save DTR to scene
    def save_dtr_to_scene(self, scene: int) -> None:
        """Save DTR to scene."""
        check_value_range(scene, 1, 16, "scene")
        self._send_config_command(0b01000000 + scene)

    # 80-95. Remove from scene
    def remove_from_scene(self, scene: int) -> None:
        """Remove from scene."""
        check_value_range(scene, 1, 16, "scene")
        self._send_config_command(0b01010000 + scene)

    # 96-111. Add to group
    def add_to_group(self, group: int) -> None:
        """Add to group."""
        check_value_range(group, 1, 16, "group")
        self._send_config_command(0b01100000 + group)

    # 112-127. Remove from group
    def remove_from_group(self, group: int) -> None:
        """Remove from group."""
        check_value_range(group, 1, 16, "group")
        self._send_config_command(0b01110000 + group)

    # 128. Save DTR as short address
    def save_dtr_as_short_address(self) -> None:
        """Save DTR as short address."""
        self._send_config_command(0b10000000)

    # 160. Get current value
    def get_current_value(self) -> int:
        """Get current value."""
        return self._read_command(0b10100000)

    # 161. Get max value
    def get_max_value(self) -> int:
        """Get max value."""
        return self._read_command(0b10100001)

    # 162. Get min value
    def get_min_value(self) -> int:
        """Get min value."""
        return self._read_command(0b10100010)

    # 163. Get power on value
    def get_power_on_value(self) -> int:
        """Get power on value."""
        return self._read_command(0b10100011)

    # 164. Get system error value
    def get_system_error_value(self) -> int:
        """Get system error value."""
        return self._read_command(0b10100100)

    # 165. Get step time and speed
    def get_step_time_and_speed(self) -> int:
        """Get step time and speed."""
        return self._read_command(0b10100101)

    # 166-175. Reserved

    # 176-191. Get scene value
    def get_scene_value(self, scene: int) -> int:
        """Get scene value."""
        check_value_range(scene, 0, 15, "scene")
        return self._read_command(0b10110000 + scene)

    # 192-193. Get group membership
    def get_groups(self) -> list[int]:
        """Get groups."""
        # Get Group 1-8
        groups = [i for bit, i in iterate_bits(self._read_command(0b11000000)) if bit]
        # Get Group 9-16
        groups.extend(
            [i for bit, i in iterate_bits(self._read_command(0b11000001)) if bit]
        )
        return groups

    # 194-196. Get direct address
    def get_direct_address(self) -> int:
        """Get direct address."""
        # Get lower 8 bit address
        high_byte = self._read_command(0b11000010)
        # Get middle 8 bit address
        middle_byte = self._read_command(0b11000011)
        # Get upper 8 bit address
        low_byte = self._read_command(0b11000100)
        return high_byte << 24 | middle_byte << 16 | low_byte

    # 197-223. Reserved

    # 224-255. Get application specific extension commands
    def get_application_specific_extension_commands(
        self, extension_command: int
    ) -> int:
        """Get application specific extension commands."""
        check_value_range(extension_command, 0, 63, "extension_command")
        return self._read_command(0b11000000 + extension_command)

    # 999. WAGO specific: Direct brightness control
    def set_brightness(self, brightness: int) -> None:
        """Set brightness."""
        check_value_range(brightness, 0, 254, "brightness")
        self.dali_communication_register.write(
            DaliOutputMessage(dali_address=self.dali_address, brightness=brightness)
        )

    # Macro Commands

    # 1. Save scene/parameter
    def save_scene_parameter(self) -> None:
        """Save scene parameter."""
        self._send_extended_command(0x01)

    # 2. Reassign short address
    def reassignment_short_address(self) -> None:
        """Reassignment short address."""
        self._send_extended_command(0x02)

    # 3. Delete short address
    def delete_short_address(self) -> None:
        """Delete short address."""
        self._send_extended_command(0x03)

    # 4. Replace short address
    def replace_short_address(self) -> None:
        """Replace short address."""
        self._send_extended_command(0x04)

    # 5. Blink show address [sec]
    def blink_show_address(self, seconds: int) -> None:
        """Blink show address."""
        check_value_range(seconds, 0, 255, "seconds")
        timeout = seconds + 1
        self._send_extended_command(0x05, parameter_1=seconds, timeout=timeout)
