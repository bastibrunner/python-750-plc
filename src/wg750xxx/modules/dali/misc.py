"""Misc functions."""

from collections.abc import Generator


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
