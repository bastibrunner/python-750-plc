"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods
from typing import Any

from .dali_communication import (
    DaliCommunicationRegister,
    DaliInputMessage,
    DaliOutputMessage,
)
from .misc import check_value_range, iterate_bits


class DaliChannelCommands:
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

    @property
    def brightness(self) -> int:
        """Get the brightness value."""
        return self.get_current_value()

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Set the brightness value."""
        self.set_brightness(value)

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

    def _read_command(self, command_code: int) -> DaliInputMessage | None:
        """Read a command from the DALI channel."""
        return self.dali_communication_register.write(
            DaliOutputMessage(
                dali_address=self.dali_address, command_code=command_code
            ),
            response=True,
        )

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

    # 5. Get current max value
    def get_current_max_value(self) -> int:
        """Get current max value."""
        self._send_command(0b00000101)
        return self.dali_communication_register.read().dali_response

    # 6. Get current min value
    def get_current_min_value(self) -> None:
        """Get current min value."""
        self._send_command(0b00000110)

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

    # 32. Reset
    def reset(self) -> None:
        """Reset."""
        self._send_config_command(0b00100000)

    # 33. Save current value to DTR
    def save_current_value_to_dtr(self) -> None:
        """Save current value to DTR."""
        self._send_config_command(0b00100001)

    # 34-41. Reserved

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

    # 48-63. Reserved

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

    # 129-143. Reserved

    # 144. Get status
    def get_status(self) -> int:
        """Get status."""
        return self._read_command(0b10010000).dali_response

    # 145. Get power supply
    def get_power_supply(self) -> int:
        """Get power supply."""
        return self._read_command(0b10010001).dali_response

    # 146. Get lamp failure
    def get_lamp_failure(self) -> int:
        """Get lamp failure."""
        return self._read_command(0b10010010).dali_response

    # 147. Get power supply lamp on
    def get_power_supply_lamp_on(self) -> int:
        """Get power supply lamp on."""
        return self._read_command(0b10010011).dali_response

    # 148. Get limit error
    def get_limit_error(self) -> int:
        """Get limit error."""
        return self._read_command(0b10010100).dali_response

    # 149. Get reset status
    def get_reset_status(self) -> int:
        """Get reset status."""
        return self._read_command(0b10010101).dali_response

    # 150. Get short address missing
    def get_short_address_missing(self) -> int:
        """Get short address missing."""
        return self._read_command(0b10010110).dali_response

    # 151. Get version number
    def get_version_number(self) -> int:
        """Get version number."""
        return self._read_command(0b10010111).dali_response

    def get_dtr_content(self) -> int:
        """Get DTR content."""
        return self._read_command(0b10011000).dali_response

    # 153. Get device type
    def get_device_type(self) -> int:
        """Get device type."""
        return self._read_command(0b10011001).dali_response

    # 154. Get physical min value
    def get_physical_min_value(self) -> int:
        """Get physical min value."""
        return self._read_command(0b10011010).dali_response

    # 155. Get power supply error
    def get_power_supply_error(self) -> int:
        """Get power supply error."""
        return self._read_command(0b10011011).dali_response

    # 156-159. Reserved

    # 160. Get current value
    def get_current_value(self) -> int:
        """Get current value."""
        return self._read_command(0b10100000).dali_response

    # 161. Get max value
    def get_max_value(self) -> int:
        """Get max value."""
        return self._read_command(0b10100001).dali_response

    # 162. Get min value
    def get_min_value(self) -> int:
        """Get min value."""
        return self._read_command(0b10100010).dali_response

    # 163. Get power on value
    def get_power_on_value(self) -> int:
        """Get power on value."""
        return self._read_command(0b10100011).dali_response

    # 164. Get system error value
    def get_system_error_value(self) -> int:
        """Get system error value."""
        return self._read_command(0b10100100).dali_response

    # 165. Get step time and speed
    def get_step_time_and_speed(self) -> int:
        """Get step time and speed."""
        return self._read_command(0b10100101).dali_response

    # 166-175. Reserved

    # 176-191. Get scene value
    def get_scene_value(self, scene: int) -> int:
        """Get scene value."""
        check_value_range(scene, 0, 15, "scene")
        return self._read_command(0b10110000 + scene).dali_response

    # 192-193. Get group membership
    def get_groups(self) -> list[int]:
        """Get groups."""
        # Get Group 1-8
        groups = [
            i
            for bit, i in iterate_bits(self._read_command(0b11000000).dali_response)
            if bit
        ]
        # Get Group 9-16
        groups.extend(
            [
                i
                for bit, i in iterate_bits(self._read_command(0b11000001).dali_response)
                if bit
            ]
        )
        return groups

    # 194-196. Get direct address
    def get_direct_address(self) -> int:
        """Get direct address."""
        # Get lower 8 bit address
        high_byte = self._read_command(0b11000010).dali_response
        # Get middle 8 bit address
        middle_byte = self._read_command(0b11000011).dali_response
        # Get upper 8 bit address
        low_byte = self._read_command(0b11000100).dali_response
        return high_byte << 24 | middle_byte << 16 | low_byte

    # 197-223. Reserved

    # 224-255. Get application specific extension commands
    def get_application_specific_extension_commands(
        self, extension_command: int
    ) -> int:
        """Get application specific extension commands."""
        check_value_range(extension_command, 0, 63, "extension_command")
        return self._read_command(0b11000000 + extension_command).dali_response

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
