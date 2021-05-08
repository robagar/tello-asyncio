from collections import namedtuple
from enum import Enum


Range = namedtuple('Range', 'low high')

Vector = namedtuple('Vector', 'x y z')

TelloState = namedtuple('TelloState', 'raw roll pitch yaw height barometer battery time_of_flight motor_time temperature acceleration velocity mission_pad mission_pad_position')

class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    FORWARD = 'forward'
    BACK = 'back'

class MissionPadDetection(Enum):
    DOWN = 0
    FORWARD = 1
    BOTH = 2 