"""Registers module contains the classes for the words and bits of the Modbus registers."""

from collections.abc import Iterator
from types import EllipsisType
from typing import Self

import numpy as np


class Words:
    """A class to represent a Modbus word (16-bit) register of any length."""

    def __init__(
        self,
        words: list[int]
        | np.ndarray[tuple[int, ...], np.dtype[np.uint16]]
        | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Words class."""
        if words is None:
            self._words = np.array([], dtype=np.uint16)
        elif isinstance(words, np.ndarray):
            self._words = words
        else:
            self._words = np.array(words, dtype=np.uint16)
        if size == 0:
            size = self._words.size
        # padding with zeros if width is greater than the number of words given
        if size > self._words.size:
            self._words = np.pad(
                self._words,
                (0, size - len(self._words)),
                mode="constant",
                constant_values=0,
            )
        elif size < self._words.size:
            self._words = self._words[:size]
        self.width: int = self._words.size

    def copy(self) -> Self:
        """Copy the word register."""
        return Words(self._words.copy())

    def __str__(self) -> str:
        """Get the string representation of the word register."""
        return self.value_to_hex()

    def __repr__(self) -> str:
        """Get the string representation of the word register."""
        return f"{self._words}"

    @property
    def value(self) -> list[int]:
        """Get the content of the word register."""
        return self._words.tolist()

    @value.setter
    def value(self, value: list[int]) -> None:
        self._words[...] = np.array(value, dtype=np.uint16)

    # def value(self, value: list[int], start: int = 0):
    #     self._words = self._words[:start] + value + self._words[start+len(value):]

    def value_to_hex(self) -> str:
        """Get the word register content as hexadecimal string representation."""
        return "".join([f"{b:04X}" for b in self._words])

    def value_to_bin(self) -> str:
        """Get the word register content as binary string representation."""
        return "".join([f"{b:016b}" for b in self._words])

    def value_to_int(self) -> int:
        """Get the word register content as integer representation."""
        if self._words.size > 1:
            return int(sum((int(b) << (16 * i) for i, b in enumerate(self._words)), 0))
        return int(self._words[0])

    def __int__(self) -> int:
        """Get the word register content as integer representation."""
        return self.value_to_int()

    def value_to_float(self) -> float:
        """Get the word register content as float representation."""
        # TODO: Implement this properly
        return float(self.value_to_int())

    def value_to_string(self) -> str:
        """Get the word register content as string representation."""
        return "".join(
            [f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._words if b != 0]
        ).rstrip("\x00")

    def __getitem__(self, index: slice | int) -> Self:
        """Get the word register content at a specific index or slice."""
        if isinstance(index, slice):
            return Words(self._words[index])
        if isinstance(index, int):
            return Words([self._words[index]])
        raise ValueError(f"Invalid index type: {type(index)}")

    def __setitem__(
        self, index: int | slice | EllipsisType, value: int | list[int]
    ) -> None:
        """Set the word register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            self._words[...] = np.array(value, dtype=np.uint16)
        else:
            self._words[index] = value

    def __len__(self) -> int:
        """Get the length of the word register."""
        return len(self._words)

    def __iter__(self) -> Iterator[int]:
        """Get the iterator of the word register."""
        return iter(self._words)

    def __next__(self) -> int:
        """Get the next word in the word register."""
        return int(next(iter(self._words)))

    def __missing__(self, index: int) -> int:
        """Get the word at a specific index."""
        return self._words[index]

    def __contains__(self, item) -> bool:
        """Check if the word register contains a specific item."""
        if isinstance(item, Words):
            return item.value.base is self.value
        return False

    def __eq__(self, other) -> bool:
        """Check if the word register is equal to another word register."""
        if not isinstance(other, Words):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._words, other.value)

    def __ne__(self, other) -> bool:
        """Check if the word register is not equal to another word register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the word register."""
        return hash(self._words)


class Bits:
    """A class to represent a Modbus one bit register of any length."""

    def __init__(
        self,
        bits: list[bool]
        | np.ndarray[tuple[int, ...], np.dtype[np.bool_]]
        | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Bits class."""
        if bits is None:
            self._bits = np.array([], dtype=bool)
        elif isinstance(bits, np.ndarray):
            self._bits = bits
        else:
            self._bits = np.array(bits, dtype=bool)
        if size == 0:
            size = len(self._bits)
        # padding with zeros if width is greater than the number of bits given
        if size > len(self._bits):
            self._bits = np.pad(
                self._bits,
                (0, size - len(self._bits)),
                mode="constant",
                constant_values=False,
            )
        elif size < len(self._bits):
            self._bits = self._bits[:size]
        self.width: int = len(self._bits)

    def copy(self) -> Self:
        """Copy the bit register."""
        return Bits(self._bits.copy())

    def __str__(self) -> str:
        """Get the string representation of the bit register."""
        return "".join([f"{b}" for b in self._bits])

    def __repr__(self) -> str:
        """Get the string representation of the bit register."""
        return f"{self._bits}"

    @property
    def value(self) -> list[bool]:
        """Get the content of the bit register."""
        return self._bits.tolist()

    @value.setter
    def value(self, value: list[bool]) -> None:
        self._bits[...] = np.array(value, dtype=bool)

    # def value(self, value: list[int], start: int = 0):
    #     self._bits = self._bits[:start] + value + self._bits[start+len(value):]

    def value_to_hex(self) -> str:
        """Get the bit register content as hexadecimal string representation."""
        return "".join([f"{b:04X}" for b in self._bits])

    def value_to_bin(self) -> str:
        """Get the bit register content as binary string representation."""
        return "".join([f"{b:016b}" for b in self._bits])

    def value_to_int(self) -> int:
        """Get the bit register content as integer representation."""
        return sum(b << (16 * i) for i, b in enumerate(self._bits))

    def value_to_float(self) -> float:
        """Get the bit register content as float representation."""
        raise NotImplementedError

    def value_to_string(self) -> str:
        """Get the bit register content as string representation."""
        return "".join(
            [f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._bits if b != 0]
        ).rstrip("\x00")

    def __getitem__(self, index: slice | int) -> Self | list[Self]| bool:
        """Get the bit register content at a specific index or slice."""
        if isinstance(index, slice):
            return Bits(self._bits[index])
        if isinstance(index, int):
            return self._bits[index]
        raise ValueError(f"Invalid index type: {type(index)}")

    def __setitem__(
        self, index: int | slice | EllipsisType, value: int | list[int]
    ) -> None:
        """Set the bit register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            self._bits[...] = np.array(value, dtype=bool)
        else:
            self._bits[index] = value

    def __len__(self) -> int:
        """Get the length of the bit register."""
        return len(self._bits)

    def __iter__(self) -> Iterator[np.bool_]:
        """Get the iterator of the bit register."""
        return iter(self._bits)

    def __next__(self):
        """Get the next bit in the bit register."""
        return next(self._bits)

    def __missing__(self, index: int):
        """Get the bit at a specific index."""
        return self._bits[index]

    def __contains__(self, item) -> bool:
        """Check if the bit register contains a specific item."""
        if isinstance(item, Words):
            return item.value.base is self.value
        return False

    def __eq__(self, other) -> bool:
        """Check if the bit register is equal to another bit register."""
        if not isinstance(other, Words):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._bits, other.value)

    def __ne__(self, other) -> bool:
        """Check if the bit register is not equal to another bit register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the bit register."""
        return hash(self._bits)


class Register(Words):
    """A class to represent a Modbus register with an address."""

    def __init__(self, address: int | None, words: list[int]) -> None:
        """Initialize the Register class."""
        self.address: int | None = address
        super().__init__(words)

    def __str__(self) -> str:
        """Get the string representation of the register."""
        if self.width > 0:
            return f"Address: 0x{self.address:04X}, Value: 0x{self.value_to_hex()}"
        return f"Address: 0x{self.address:04X}, Value: N/A"

    def __repr__(self) -> str:
        """Get the string representation of the register."""
        return f"0x{self.address:04X}:0x{self._words:04X}"

    def __eq__(self, other) -> bool:
        """Check if the register is equal to another register."""
        return self.address == other.address and self._words == other.value

    def __ne__(self, other) -> bool:
        """Check if the register is not equal to another register."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Get the hash of the register."""
        return hash(self.address) ^ hash(self._words)


test_constants = [
    Register(0x2000, [0x0000]),
    Register(0x2001, [0xFFFF]),
    Register(0x2002, [0x1234]),
    Register(0x2003, [0xAAAA]),  # Maske 1, GP_AAAA
    Register(0x2004, [0x5555]),  # Maske 1, GP_5555
    Register(0x2005, [0x7FFF]),  # GP_MIN_POS
    Register(0x2006, [0x8000]),  # GP_MAX_NEG
    Register(0x2007, [0x3FFF]),  # GP_HALF_POS
    Register(0x2008, [0x4000]),  # GP_HALF_NEG
]
