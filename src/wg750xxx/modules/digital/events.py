"""Events for the Digital module."""

from enum import Enum
import asyncio
import time
from typing import Any, Callable, Optional, Set

from wg750xxx.modules.digital.channels import DigitalIn
