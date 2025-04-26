"""Registers module contains the classes for the words and bits of the Modbus registers."""

from collections.abc import Iterator
from types import EllipsisType
from typing import Self

import numpy as np

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



class Bytes:
    """A class to represent a Modbus byte (8-bit) register of any length.

    Args:
        value:  The value to initialize the byte register with. Can be a
                list of integers, a numpy array of integers, an integer or None.
                Integer values higher than 255 will be split into multiple bytes.
                If the value is None, the byte register will be initialized to an
                empty array with the size provided.
        size:   The size of the byte register. If not provided, the size will be
                the size of the value. If the size is greater than the size of the
                value, the byte register will be padded with zeros. If the size is
                less than the size of the value, the byte register will be truncated.
    """

    def __init__(self, value: list[int] | np.ndarray[tuple[int, ...], np.dtype[np.uint8]] | int | None = None, size: int = 0) -> None:
        """Initialize the Bytes class."""
        if value is None:
            self._bytes = np.array([], dtype=np.uint8)
        elif isinstance(value, np.ndarray):
            self._bytes = value
        elif isinstance(value, int):
            self._bytes = self._from_int(value)
        else:
            self._bytes = np.array(value, dtype=np.uint8)
        if size == 0:
            size = len(self._bytes)
        # padding with zeros if width is greater than the number of bytes given
        if size > len(self._bytes):
            self._bytes = np.pad(
                self._bytes,
                (0, size - len(self._bytes)),
                mode="constant",
                constant_values=0,
            )
        elif size < len(self._bytes):
            self._bytes = self._bytes[:size]
        self.width: int = len(self._bytes)

    def _from_int(self, value: int, byteorder: str = "little") -> "Bytes":
        """Convert an integer to a byte register."""
        if value < 256:
            return Bytes(np.array([value], dtype=np.uint8))
        else:
            # split the integer into bytes
            values = np.array([], dtype=np.uint8)
            if byteorder == "big":
                while value > 0:
                    values = np.insert(values, 0, value & 0xFF)
                    value >>= 8
            else:
                while value > 0:
                    values = np.append(values, value & 0xFF)
                    value >>= 8
            return Bytes(values)

    def __len__(self) -> int:
        """Get the length of the byte register."""
        return len(self._bytes)

    @property
    def value(self) -> list[int]:
        """Get the content of the byte register."""
        return self._bytes.tolist()

    @value.setter
    def value(self, value: list[int]) -> None:
        if len(value) != self._bytes.size:
            raise ValueError(f"Invalid value length, register has {self._bytes.size} bytes, got {len(value)}")
        self._bytes[...] = np.array(value, dtype=np.uint8)

    def __str__(self) -> str:
        """Get the string representation of the byte register."""
        return self.value_to_hex()

    def __repr__(self) -> str:
        """Get the string representation of the byte register."""
        return f"{self._bytes}"

    def copy(self) -> "Bytes":
        """Copy the byte register."""
        return Bytes(self._bytes.copy())

    def value_to_hex(self) -> str:
        """Get the byte register content as hexadecimal string representation."""
        return "".join([f"{b:02X}" for b in self._bytes])

    def value_to_bin(self) -> str:
        """Get the byte register content as binary string representation."""
        return "".join([f"{b:08b}" for b in self._bytes])

    def value_to_int(self, byteorder: str = "little") -> int:
        """Get the byte register content as integer representation."""
        return int.from_bytes(self._bytes, byteorder=byteorder)

    def bits(self) -> Bits:
        """Get the byte register content as bit register."""
        bit_list = []
        for byte in self._bytes:
            for i in range(7, -1, -1):
                bit_list.append(bool((byte >> i) & 1))
        return Bits(bit_list)

    def __int__(self) -> int:
        """Get the byte register content as integer representation."""
        return self.value_to_int()

    def value_to_float(self) -> float:
        """Get the byte register content as float representation."""
        return float(self.value_to_int())

    def value_to_string(self) -> str:
        """Get the byte register content as string representation."""
        return "".join([f"{chr(b & 0x00FF)}{chr(b >> 8)}" for b in self._bytes if b != 0]
        ).rstrip("\x00")

    def __getitem__(self, index: slice | int) -> "Bytes":
        """Get the byte register content at a specific index or slice."""
        if isinstance(index, slice):
            return Bytes(self._bytes[index])
        if isinstance(index, int):
            return Bytes([self._bytes[index]])
        raise ValueError(f"Invalid index type: {type(index)}")

    def __setitem__(self, index: int | slice | EllipsisType, value: int | list[int]) -> None:
        """Set the byte register content at a specific index or slice."""
        if isinstance(index, EllipsisType):
            self._bytes[...] = np.array(value, dtype=np.uint8)
        else:
            self._bytes[index] = value

    def __eq__(self, other) -> bool:
        """Check if the byte register is equal to another byte register."""
        if not isinstance(other, Bytes):
            return False
        if self.width != other.width:
            return False
        return np.array_equal(self._bytes, other.value)

    def __ne__(self, other) -> bool:
        """Check if the byte register is not equal to another byte register."""
        return not self.__eq__(other)

    def __iter__(self) -> Iterator[int]:
        """Get the iterator of the byte register."""
        return iter(self._bytes)

    def __next__(self) -> int:
        """Get the next byte in the byte register."""
        return int(next(iter(self._bytes)))


class Words:
    """A class to represent a Modbus word (16-bit) register of any length.

    Args:
        value:  The value to initialize the word register with. Can be a
                list of integers, a numpy array of integers, an integer or None.
                Integer values higher than 65535 will be split into multiple words.
                If the value is None, the word register will be initialized to an
                empty array with the size provided.
        size:   The size of the word register. If not provided, the size will be
                the size of the value. If the size is greater than the size of the
                value, the word register will be padded with zeros. If the size is
                less than the size of the value, the word register will be truncated.
    """

    def __init__(
        self,
        value: list[int] | np.ndarray[tuple[int, ...], np.dtype[np.uint16]] | int | None = None,
        size: int = 0,
    ) -> None:
        """Initialize the Words class."""
        if value is None:
            self._words = np.array([], dtype=np.uint16)
        elif isinstance(value, np.ndarray):
            self._words = value
        elif isinstance(value, int):
            self._words = self._from_int(value)
        else:
            self._words = np.array(value, dtype=np.uint16)
        if size == 0:
            size = len(self._words)
        # padding with zeros if width is greater than the number of words given
        if size > len(self._words):
            self._words = np.pad(
                self._words,
                (0, size - len(self._words)),
                mode="constant",
                constant_values=0,
            )
        elif size < len(self._words):
            self._words = self._words[:size]
        self.width: int = len(self._words)

    def _from_int(self, value: int) -> "Words":
        """Convert an integer to a word register."""
        if value < 65536:
            return Words(np.array([value], dtype=np.uint16))
        else:
            # split the integer into bytes
            values = np.array([], dtype=np.uint16)
            while value > 0:
                values = np.insert(values, 0, value & 0xFFFF)
                value >>= 16
            return Words(values)

    def copy(self) -> "Words":
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
        if len(value) != self._words.size:
            raise ValueError(f"Invalid value length, register has {self._words.size} words, got {len(value)}")
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
            return self.bytes("little").value_to_int("big")
        return int(self._words[0])

    def bits(self) -> Bits:
        """Get the word register content as bit register."""
        bit_list = []
        for word in self._words:
            for i in range(15, -1, -1):
                bit_list.append(bool((word >> i) & 1))
        return Bits(bit_list)

    def bytes(self, byteorder: str = "little") -> Bytes:
        """Convert the word register to a byte register."""
        byte_list = []
        if byteorder == "big":
            words = reversed(self._words)
        else:
            words = self._words
        for word in words:
            high_byte = (word >> 8) & 0xFF
            low_byte = word & 0xFF
            if byteorder == "big":
                byte_list.append(low_byte)
                byte_list.append(high_byte)
            else:
                byte_list.append(high_byte)
                byte_list.append(low_byte)
        return Bytes(byte_list)

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
