from collections import namedtuple

Range = namedtuple('Range', 'low high')

Vector = namedtuple('Vector', 'x y z')

TelloState = namedtuple('TelloState', 'raw roll pitch yaw height barometer battery time_of_flight motor_time temperature acceleration velocity')
