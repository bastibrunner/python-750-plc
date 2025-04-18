"""Modules."""

from .analog.modules import (
    Wg750AnalogIn1Ch,
    Wg750AnalogIn2Ch,
    Wg750AnalogIn4Ch,
    Wg750AnalogIn8Ch,
    Wg750AnalogOut2Ch,
    Wg750AnalogOut4Ch,
)
from .controller.modules import Wg750FeldbuskopplerEthernet
from .counter.modules import Wg750Counter
from .dali.modules import Wg750DaliMaster
from .digital.modules import Wg750DigitalIn, Wg750DigitalOut

__all__ = [
    "Wg750AnalogIn1Ch",
    "Wg750AnalogIn2Ch",
    "Wg750AnalogIn4Ch",
    "Wg750AnalogIn8Ch",
    "Wg750AnalogOut2Ch",
    "Wg750AnalogOut4Ch",
    "Wg750Counter",
    "Wg750DaliMaster",
    "Wg750DigitalIn",
    "Wg750DigitalOut",
    "Wg750FeldbuskopplerEthernet",
]
