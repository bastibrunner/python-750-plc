"""Dali commands."""

# pylint: disable=unused-variable,too-many-public-methods

from .channel_base import DaliChannelBase


class DaliChannelStatus(DaliChannelBase):
    """DALI commands."""

    # 144. Get status
    def get_status(self) -> int:
        """Get status."""
        return self._read_command(0b10010000)

    # 145. Get power supply
    def get_power_supply(self) -> int:
        """Get power supply."""
        return self._read_command(0b10010001)

    # 146. Get lamp failure
    def get_lamp_failure(self) -> int:
        """Get lamp failure."""
        return self._read_command(0b10010010)

    # 147. Get power supply lamp on
    def get_power_supply_lamp_on(self) -> int:
        """Get power supply lamp on."""
        return self._read_command(0b10010011)

    # 148. Get limit error
    def get_limit_error(self) -> int:
        """Get limit error."""
        return self._read_command(0b10010100)

    # 149. Get reset status
    def get_reset_status(self) -> int:
        """Get reset status."""
        return self._read_command(0b10010101)

    # 150. Get short address missing
    def get_short_address_missing(self) -> int:
        """Get short address missing."""
        return self._read_command(0b10010110)

    # 151. Get version number
    def get_version_number(self) -> int:
        """Get version number."""
        return self._read_command(0b10010111)

    def get_dtr_content(self) -> int:
        """Get DTR content."""
        return self._read_command(0b10011000)

    # 153. Get device type
    def get_device_type(self) -> int:
        """Get device type."""
        return self._read_command(0b10011001)

    # 154. Get physical min value
    def get_physical_min_value(self) -> int:
        """Get physical min value."""
        return self._read_command(0b10011010)

    # 155. Get power supply error
    def get_power_supply_error(self) -> int:
        """Get power supply error."""
        return self._read_command(0b10011011)

    # 156-159. Reserved
