from collections import namedtuple
from enum import Enum


Range = namedtuple('Range', 'low high')
Range.low.__doc__ = 'minimum value'
Range.high.__doc__ = 'maximum value'

Vector = namedtuple('Vector', 'x y z')
Vector.x.__doc__ = 'x value' 
Vector.y.__doc__ = 'y value' 
Vector.z.__doc__ = 'z value' 

TelloState = namedtuple('TelloState', 'raw roll pitch yaw height barometer battery time_of_flight motor_time temperature acceleration velocity mission_pad mission_pad_position')
TelloState.raw.__doc__ = 'Raw state message string'
TelloState.roll.__doc__ = 'Rotation in degrees around the drone\'s local y axis'
TelloState.pitch.__doc__ = 'Rotation in degrees around the drone\'s local x axis'
TelloState.yaw.__doc__ = 'Rotation in degrees around the drone\'s local z axis'
TelloState.height.__doc__ = 'Height in cm'
TelloState.barometer.__doc__ = 'Atmospheric pressure'
TelloState.battery.__doc__ = 'Remaining battery percentage'
TelloState.time_of_flight.__doc__ = 'Time of flight returned by the height sensor'
TelloState.motor_time.__doc__ = 'Time in seconds the motors have been active for'
TelloState.temperature.__doc__ = 'Range in temperature in degrees Celsius'
TelloState.acceleration.__doc__ = ':class:`tello_asyncio.types.Vector` acceleration in cm/s/s in each axis direction'
TelloState.velocity.__doc__ = ':class:`tello_asyncio.types.Vector` speed in cm/s in each axis direction'
TelloState.mission_pad.__doc__ = 'Mission pad ID'
TelloState.mission_pad_position.__doc__ = ':class:`tello_asyncio.types.Vector` mission pad relative posistion'


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