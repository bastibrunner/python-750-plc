"""Test the Modbus registers functionality."""

# pylint: disable=protected-access,redefined-outer-name
import numpy as np
import pytest

from wg750xxx.modbus.registers import Bits, Bytes, Words

# ruff: noqa: SLF001


def test_words_copy_method():
    """Test that the Words.copy() method returns a new Words instance."""
    # Create a Words instance
    original_words = Words(np.array([1, 2, 3, 4], dtype=np.uint16))

    # Copy the words
    copied_words = original_words.copy()

    # Verify the copy is a new Words instance with the same values
    assert isinstance(copied_words, Words)
    assert np.array_equal(original_words._words, copied_words._words)
    assert original_words is not copied_words

    # Modify the original and verify the copy is unchanged
    original_words._words[0] = 10
    assert original_words._words[0] == 10
    assert copied_words._words[0] == 1


def test_bytes_copy_method():
    """Test that the Bytes.copy() method returns a new Bytes instance."""
    # Create a Bytes instance
    original_bytes = Bytes(np.array([1, 2, 3, 4], dtype=np.uint8))

    # Copy the bytes
    copied_bytes = original_bytes.copy()

    # Verify the copy is a new Bytes instance with the same values
    assert isinstance(copied_bytes, Bytes)
    assert np.array_equal(original_bytes._bytes, copied_bytes._bytes)
    assert original_bytes is not copied_bytes

    # Modify the original and verify the copy is unchanged
    original_bytes._bytes[0] = 10
    assert original_bytes._bytes[0] == 10
    assert copied_bytes._bytes[0] == 1


def test_bits_copy_method():
    """Test that the Bits.copy() method returns a new Bits instance."""
    # Create a Bits instance
    original_bits = Bits(np.array([True, False, True, False], dtype=np.bool))

    # Copy the bits
    copied_bits = original_bits.copy()

    # Verify the copy is a new Bits instance with the same values
    assert isinstance(copied_bits, Bits)
    assert np.array_equal(original_bits._bits, copied_bits._bits)
    assert original_bits is not copied_bits

    # Modify the original and verify the copy is unchanged
    original_bits._bits[0] = False
    assert original_bits._bits[0] == False  # noqa: E712 # disabling ruff qa rule for better visibility
    assert copied_bits._bits[0] == True  # noqa: E712 # disabling ruff qa rule for better visibility


def test_bits_to_bytes_method():
    """Test that the Bits.to_bytes() method returns a Bytes instance."""
    # Create a Bits instance
    bits_instance = Bits([True, False, True, False])

    # Convert the bits to a Bytes instance
    bytes_instance = bits_instance.value_to_bytes()

    # Verify the Bytes instance is a new Bytes instance with the correct values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 1
    assert bytes_instance.value.tolist() == [0b0101]

    bits_instance = Bits(
        [
            True,
            False,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
        ]
    )

    # Convert the bits to a Bytes instance
    bytes_instance = bits_instance.value_to_bytes()

    # Verify the Bytes instance is a new Bytes instance with the correct values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 2
    assert bytes_instance.value.tolist() == [0b00111001, 0b11100101]

    # Convert the bits to a Bytes instance
    bytes_instance = bits_instance.value_to_bytes(byteorder="little")

    # Verify the Bytes instance is a new Bytes instance with the correct values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 2
    assert bytes_instance.value.tolist() == [0b11100101, 0b00111001]

    # Convert the bits to a Bytes instance
    bytes_instance = bits_instance.value_to_bytes(byteorder="big")

    # Verify the Bytes instance is a new Bytes instance with the correct values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 2
    assert bytes_instance.value.tolist() == [0b00111001, 0b11100101]


def test_bits_to_words_method():
    """Test that the Bits.to_words() method returns a Words instance."""
    # Create a Bits instance
    bits_instance = Bits(
        [
            True,
            False,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
        ]
    )

    # Convert the bits to a Words instance
    words_instance = bits_instance.value_to_words()

    # Verify the Words instance is a new Words instance with the correct values
    assert isinstance(words_instance, Words)
    assert len(words_instance) == 1
    assert words_instance.value.tolist() == [0b0011100111100101]

    words_instance = bits_instance.value_to_words(wordorder="little")

    # Verify the Words instance is a new Words instance with the correct values
    assert isinstance(words_instance, Words)
    assert len(words_instance) == 1
    assert words_instance.value.tolist() == [0b0011100111100101]

    words_instance = bits_instance.value_to_words(wordorder="big")

    # Verify the Words instance is a new Words instance with the correct values
    assert isinstance(words_instance, Words)
    assert len(words_instance) == 1
    assert words_instance.value.tolist() == [0b0011100111100101]


def test_bits_to_int_method():
    """Test that the Bits.to_int() method returns an integer."""
    # Create a Bits instance
    bits_instance = Bits([True, False, True, True, False, False, True, True])

    # Convert the bits to an integer
    int_instance = bits_instance.value_to_int()

    # Verify the integer is a new integer with the correct value
    assert isinstance(int_instance, int)
    assert int_instance == 0b11001101
    assert int_instance == int(bits_instance)


def test_bits_to_int_method_with_byte_order():
    """Test that the Bits.to_int() method returns an integer with the correct byte order."""
    # Create a Bits instance
    bits_instance = Bits(
        [
            True,
            False,
            True,
            False,
            False,
            True,
            True,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
        ]
    )

    # Convert the bits to an integer with the correct byte order
    int_instance = bits_instance.value_to_int(byteorder="big")
    assert isinstance(int_instance, int)
    assert int_instance == 0b0011100111100101
    int_instance = bits_instance.value_to_int(byteorder="little")
    assert isinstance(int_instance, int)
    assert int_instance == 0b1110010100111001


def test_words_to_bytes_method():
    """Test that the Words.to_bytes() method returns a Bytes instance."""
    # Create a Words instance
    words_instance = Words([0x01FF, 0x02FF])
    # Convert the words to a Bytes instance
    bytes_instance = words_instance.bytes()
    # Verify the Bytes instance is a new Bytes instance with the same values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 4
    assert bytes_instance.value.tolist() == [0x01, 0xFF, 0x02, 0xFF]


def test_words_to_bytes_method_with_byte_order():
    """Test that the Words.to_bytes() method returns a Bytes instance with the correct byte order."""
    # Create a Words instance
    words = Words([0x01FF, 0x02FF])

    # Convert the words to a Bytes instance with the correct byte order
    bytes_instance = words.bytes(byteorder="big")

    # Verify the Bytes instance is a new Bytes instance with the correct byte order
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 4
    assert bytes_instance.value.tolist() == [0xFF, 0x02, 0xFF, 0x01]


@pytest.mark.parametrize(
    "testvalues",
    [
        {
            "words": Words([0x00FF]),
            "expected_int_big": 0x00FF,
            "expected_int_little": 0xFF00,
        },
        {
            "words": Words([0x12FF]),
            "expected_int_big": 0x12FF,
            "expected_int_little": 0xFF12,
        },
        {
            "words": Words([0x001F, 0x12FF]),
            "expected_int_big": 0x001F12FF,
            "expected_int_little": 0xFF121F00,
        },
        {
            "words": Words([0x0C06, 0x0000]),
            "expected_int_big": 0x0C060000,
            "expected_int_little": 0x0000060C,
        },
    ],
)
def test_words_to_int_method(testvalues: dict[str, Words | int]) -> None:
    """Test that the Words.to_int() method returns an integer."""
    # Create a Words instance
    words = testvalues["words"]
    assert isinstance(words, Words)
    assert words.value_to_int(byteorder="big") == testvalues["expected_int_big"], (
        f"Failed for {testvalues['words']} with big endian word order: Expected {testvalues['expected_int_big']:0X} but got {words.value_to_int(byteorder='big'):0X}"
    )
    assert (
        words.value_to_int(byteorder="little") == testvalues["expected_int_little"]
    ), (
        f"Failed for {testvalues['words']} with little endian word order: Expected {testvalues['expected_int_little']:0X} but got {words.value_to_int(byteorder='little'):0X}"
    )
    assert words.value_to_int() == testvalues["expected_int_big"], (
        f"Failed for {testvalues['words']} with default (big) endian word order: Expected {testvalues['expected_int_big']:0X} but got {words.value_to_int():0X}"
    )


def test_int_to_words_method():
    """Test that the int_to_words() method returns a Words instance."""
    # Create a Words instance
    words = Words(0x001234567890)
    assert words == Words([0x0012, 0x3456, 0x7890]), (
        f"Failed for 0x001234567890: Expected Words([0x0012, 0x3456, 0x7890]) but got {words}"
    )


def test_bytes_to_int_method():
    """Test that the Bytes.to_int() method returns an integer."""
    # Create a Bytes instance
    bytes_instance = Bytes([0xFF])
    assert bytes_instance.value_to_int() == 0xFF, (
        f"Failed for Bytes([0xFF]): Expected {0xFF} but got {bytes_instance.value_to_int()}"
    )
    assert bytes_instance.value_to_int(byteorder="big") == 0xFF, (
        f"Failed for Bytes([0xFF]): Expected {0xFF} but got {bytes_instance.value_to_int(byteorder='big')}"
    )
    assert bytes_instance.value_to_int(byteorder="little") == 0xFF, (
        f"Failed for Bytes([0xFF]): Expected {0xFF} but got {bytes_instance.value_to_int(byteorder='little')}"
    )

    bytes_instance = Bytes([0xF1, 0xF2, 0xF3, 0xF4, 0xF5])
    assert bytes_instance.value_to_int() == 0xF5F4F3F2F1, (
        f"Default byte order failed for Bytes([0xF1, 0xF2, 0xF3, 0xF4, 0xF5]): Expected {0xF1F2F3F4F5:0X} but got {bytes_instance.value_to_int():0X}"
    )
    assert bytes_instance.value_to_int(byteorder="big") == 0xF1F2F3F4F5, (
        f"Big endian byte order failed for Bytes([0xF1, 0xF2, 0xF3, 0xF4, 0xF5]): Expected {0xF1F2F3F4F5:0X} but got {bytes_instance.value_to_int(byteorder='big'):0X}"
    )
    assert bytes_instance.value_to_int(byteorder="little") == 0xF5F4F3F2F1, (
        f"Little endian byte order failed for Bytes([0xF1, 0xF2, 0xF3, 0xF4, 0xF5]): Expected {0xF5F4F3F2F1:0X} but got {bytes_instance.value_to_int(byteorder='little'):0X}"
    )


def test_conversion_chain() -> None:
    """Test that the conversion chain works."""

    words_instance = Words([0x011F, 0x12FF])
    bytes_instance = Bytes([0xFF, 0x12, 0x1F, 0x01])
    int_instance = 0xFF121F01

    # From words to int and back to words
    int_instance_2 = words_instance.value_to_int()
    words_instance_2 = Words(int_instance_2)
    assert words_instance == words_instance_2

    # From bytes to int and back to bytes
    int_instance_4 = bytes_instance.value_to_int()
    bytes_instance_4 = Bytes(int_instance_4)
    assert bytes_instance == bytes_instance_4

    # From int to bytes and back to int
    bytes_instance_5 = Bytes(int_instance)
    int_instance_5 = bytes_instance_5.value_to_int()
    assert int_instance == int_instance_5

    # From words to bytes and back to words
    bytes_instance_3 = words_instance.bytes(byteorder="big")
    int_instance_3 = bytes_instance_3.value_to_int(byteorder="little")
    words_instance_3 = Words(Words.from_int(int_instance_3, byteorder="big"))
    assert words_instance == words_instance_3


def test_int_to_bytes_method():
    """Test that the int_to_bytes() method returns a Bytes instance."""
    bytes_instance = Bytes.from_int(0x01F1022F, byteorder="big")
    assert bytes_instance == Bytes([0x01, 0xF1, 0x02, 0x2F]), (
        f"Failed for 0x01F1022F: Expected Bytes([0x01, 0xF1, 0x02, 0x2F]) but got {bytes_instance}"
    )
    bytes_instance = Bytes.from_int(0x01F1022F, byteorder="little")
    assert bytes_instance == Bytes([0x2F, 0x02, 0xF1, 0x01]), (
        f"Failed for 0x01F1022F: Expected Bytes([0x2F, 0x02, 0xF1, 0x01]) but got {bytes_instance}"
    )
    bytes_instance = Bytes(0x01F1022F)
    assert bytes_instance == Bytes([0x2F, 0x02, 0xF1, 0x01]), (
        f"Failed for 0x01F1022F: Expected Bytes([0x2F, 0x02, 0xF1, 0x01]) but got {bytes_instance}"
    )


def test_bytes_eq_method():
    """Test that the Bytes.__eq__() method returns a boolean."""
    # Create a Bytes instance
    bytes_instance = Bytes([0xFF, 0x00, 0xFF, 0x00, 0xFF])
    assert bytes_instance == Bytes([0xFF, 0x00, 0xFF, 0x00, 0xFF])
    assert bytes_instance != Bytes([0x00, 0xFF, 0x00, 0xFF, 0x00])


def test_words_eq_method():
    """Test that the Words.__eq__() method returns a boolean."""
    # Create a Words instance
    words_instance = Words([0xFF, 0x00, 0xFF, 0x00, 0xFF])
    assert words_instance == Words([0xFF, 0x00, 0xFF, 0x00, 0xFF])
    assert words_instance != Words([0x00, 0xFF, 0x00, 0xFF, 0x00])


def test_words_subset_method():
    """Test that the words_subset() method returns a Words instance."""
    # Create a Words instance
    words = Words([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Create a subset of the words
    subset = words[1:3]

    # Verify the subset is a new Words instance with the correct values
    assert isinstance(subset, Words), (
        f"Slice [1:3] of {words} is not a Words instance: {type(subset)}"
    )
    assert subset == Words([2, 3]), (
        f"Slice [1:3] of {words} is not the expected Words([2, 3]): {subset}"
    )
    # Changing a slice of the words updates the original
    words[1:4] = [11, 12, 13]
    assert words == Words([1, 11, 12, 13, 5, 6, 7, 8, 9, 10]), (
        f"Updating slice [1:4] to Words([11, 12, 13]) did not update the original words: {words}"
    )
    assert subset == Words([11, 12]), (
        f"Updating slice [1:4] to Words([11, 12, 13]) did not update the subset instance: {subset}"
    )
    with pytest.raises(ValueError) as error:
        words.value = [14, 15, 16, 17, 18, 19, 20]
    assert (
        str(error.value)
        == "could not broadcast input array from shape (7,) into shape (10,)"
    ), (
        "Updating words with a list of integers that has not the correct length did not raise a ValueError."
    )
    words.value = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    assert words == Words([14, 15, 16, 17, 18, 19, 20, 21, 22, 23]), (
        f"Updating Words instance did not update the instance value: {words}"
    )
    assert subset == Words([15, 16]), (
        f"Updating Words instance did not update the subset instance: {subset}"
    )
