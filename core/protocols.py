"""
Provides protocols for type hinting
"""

from typing import Protocol


class ServoPosition(Protocol):
    """
    Defines the ServoPosition protocol for objects that contain
    both a servo port and servo position value
    """

    @property
    def value(self):
        return

    @property
    def port(self):
        return
