"""Test the Modbus registers functionality."""

# pylint: disable=protected-access,redefined-outer-name
import numpy as np
import pytest

from wg750xxx.modbus.registers import Bytes, Words

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


def test_words_to_bytes_method():
    """Test that the Words.to_bytes() method returns a Bytes instance."""
    # Create a Words instance
    words_instance = Words([0x0000, 0x01FF])
    # Convert the words to a Bytes instance
    bytes_instance = words_instance.bytes()
    # Verify the Bytes instance is a new Bytes instance with the same values
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 4
    assert bytes_instance.value == [0x00, 0x00, 0x01, 0xFF]


def test_words_to_bytes_method_with_byte_order():
    """Test that the Words.to_bytes() method returns a Bytes instance with the correct byte order."""
    # Create a Words instance
    words = Words([0x01FF, 0x02FF])

    # Convert the words to a Bytes instance with the correct byte order
    bytes_instance = words.bytes(byteorder="big")

    # Verify the Bytes instance is a new Bytes instance with the correct byte order
    assert isinstance(bytes_instance, Bytes)
    assert len(bytes_instance) == 4
    assert bytes_instance.value == [0xFF, 0x02, 0xFF, 0x01]


def test_words_to_int_method():
    """Test that the Words.to_int() method returns an integer."""
    # Create a Words instance
    words = Words([0x00FF])
    assert words.value_to_int() == 0xFF
    words = Words([0xFFFF])
    assert words.value_to_int() == 0xFFFF
    words = Words([0x00FF, 0x12FF])
    assert words.value_to_int() == 0xFF12FF
    words = Words([0x00FF, 0x12FF, 0x34FF])
    assert words.value_to_int() == 0x00FF12FF34FF


def test_int_to_words_method():
    """Test that the int_to_words() method returns a Words instance."""
    # Create a Words instance
    words = Words(0x00FF00FF00FF)
    assert words == Words([0x00FF, 0x00FF, 0x00FF])


def test_bytes_to_int_method():
    """Test that the Bytes.to_int() method returns an integer."""
    # Create a Bytes instance
    bytes_instance = Bytes([0xFF, 0x00, 0xFF, 0x00, 0xFF])
    assert bytes_instance.value_to_int() == 0x00FF00FF00FF


def test_int_to_bytes_method():
    """Test that the int_to_bytes() method returns a Bytes instance."""
    # Create a Bytes instance
    bytes_instance = Bytes(0xFF00FF00FF)
    assert bytes_instance == Bytes([0xFF, 0x00, 0xFF, 0x00, 0xFF])


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
    assert isinstance(subset, Words)
    assert subset == Words([2, 3])
    words[1:4] = [11, 12, 13]
    assert words == Words([1, 11, 12, 13, 5, 6, 7, 8, 9, 10])
    assert subset == Words([11, 12])
    with pytest.raises(ValueError):
        words.value = [14, 15, 16, 17, 18, 19, 20]
    words.value = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    assert words == Words([14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
    assert subset == Words([15, 16])
