"""Misc functions."""

from collections.abc import Generator

from wg750xxx.modules.dali.dali_communication import DaliInputMessage


def iterate_bits(byte: int) -> Generator[tuple[bool, int]]:
    """Iterate over the bits of a byte."""
    for i in range(8):
        yield bool((byte >> i) & 1), i


def get_bit(byte: int, bit_index: int) -> bool:
    """Get the value of a bit in a byte."""
    return bool((byte >> bit_index) & 1)


def check_value_range(value: int, min_value: int, max_value: int, name: str) -> None:
    """Check value range."""
    if not min_value <= value <= max_value:
        raise ValueError(f"{name} must be between {min_value} and {max_value}")

def dali_response_to_channel_list(
    response: DaliInputMessage | None, offset: int = 0
) -> list[int]:
    """Convert DALI response to channel list."""
    channels: list[int] = []
    if response is None:
        return channels
    channels.extend(
        [offset + i for bit, i in iterate_bits(response.dali_response) if bit]
    )
    channels.extend([offset + 8 + i for bit, i in iterate_bits(response.message_3) if bit])
    channels.extend([offset + 16 + i for bit, i in iterate_bits(response.message_2) if bit])
    channels.extend([offset + 24 + i for bit, i in iterate_bits(response.message_1) if bit])
    return channels
