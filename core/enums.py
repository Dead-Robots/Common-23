"""
Provides enumerations that allow for type hinting
"""

from enum import IntEnum
from common.core.protocols import ServoPosition
import typing


class ServoEnum(IntEnum):
    """
    An enumeration type for servos that follow the ServoPosition protocol
    """
    pass


ServoEnum: typing.Union[ServoPosition, IntEnum]  # Fixes typing for IDE
