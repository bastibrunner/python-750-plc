"""Test the ModbusState functionality."""

# pylint: disable=protected-access,redefined-outer-name
import numpy as np

from wg750xxx.modbus.registers import Bits, Words
from wg750xxx.modbus.state import ModbusState


def test_modbus_state_get_changed_addresses() -> None:
    """Test the get_changed_addresses method with the new type annotation."""
    # Create two ModbusState instances
    state1 = ModbusState({"input": 2, "holding": 2, "discrete": 8, "coil": 8})
    state2 = ModbusState({"input": 2, "holding": 2, "discrete": 8, "coil": 8})

    # Set up state1 with some values
    state1.input = Words(np.array([0x1234, 0x5678], dtype=np.uint16))
    state1.holding = Words(np.array([0xABCD, 0xEF01], dtype=np.uint16))
    state1.discrete = Bits(
        np.array([True, False, True, False, True, False, True, False], dtype=bool)
    )
    state1.coil = Bits(
        np.array([False, True, False, True, False, True, False, True], dtype=bool)
    )

    # Set up state2 with some different values
    state2.input = Words(
        np.array([0x1234, 0x9999], dtype=np.uint16)
    )  # Changed second word
    state2.holding = Words(np.array([0xABCD, 0xEF01], dtype=np.uint16))  # Same
    state2.discrete = Bits(
        np.array([True, False, True, False, True, True, False, False], dtype=bool)
    )  # Changed bits 5,6
    state2.coil = Bits(
        np.array([False, True, False, True, False, True, False, True], dtype=bool)
    )  # Same

    # Get the changed addresses
    changed_addresses = state1.get_changed_addresses(state2)

    # Verify the changed addresses
    assert (
        1 in changed_addresses["input"]
    )  # Input register at address 1 (the second word) has changed
    assert 5 in changed_addresses["discrete"]  # Discrete input at address 5 has changed
    assert 6 in changed_addresses["discrete"]  # Discrete input at address 6 has changed

    # Verify the unchanged addresses are not in the set
    assert 0 not in changed_addresses["input"]  # First input register hasn't changed
    assert (
        2 not in changed_addresses["holding"]
    )  # First holding register hasn't changed
    assert (
        3 not in changed_addresses["holding"]
    )  # Second holding register hasn't changed
    assert 0 not in changed_addresses["discrete"]  # First discrete input hasn't changed
    assert 0 not in changed_addresses["coil"]  # First coil hasn't changed
