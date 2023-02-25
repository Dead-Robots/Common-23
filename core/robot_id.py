"""
Provides the ROBOT constant to be used to identify the robot in use
"""

from enum import Enum
from typing import Union, Tuple


class Robot(Enum):
    """
    Represents the different possible robots
    """
    BLUE = 'BLUE'
    RED = 'RED'
    GREEN = 'GREEN'
    YELLOW = 'YELLOW'

    def choose(self, choices=None, red=None, green=None, blue=None, yellow=None):
        if blue is not None and self is Robot.BLUE:
            return blue
        if red is not None and self is Robot.RED:
            return red
        if green is not None and self is Robot.GREEN:
            return green
        if yellow is not None and self is Robot.YELLOW:
            return yellow
        if choices is not None:
            try:
                return choices[self]
            except KeyError:
                pass
        raise ValueError(f"No choices provided for {self}")

    def run(self, func: callable, **kwargs: Union[Tuple, None]):
        func(*self.choose(**kwargs))

    @property
    def is_blue(self):
        return self is Robot.BLUE

    @property
    def is_red(self):
        return self is Robot.RED

    @property
    def is_green(self):
        return self is Robot.GREEN

    @property
    def is_yellow(self):
        return self is Robot.YELLOW


def _get_robot_id_from_file(path):
    try:
        with open(path, 'r') as f:
            return Robot(f.read())
    except FileNotFoundError:
        raise FileNotFoundError('The whoami.txt file was not found in the RobotID project')
    except ValueError:
        raise ValueError('A valid robot was not found in the RobotID project whoami.txt')


ROBOT = _get_robot_id_from_file("../RobotID/bin/whoami.txt")
