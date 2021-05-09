# tello-asyncio

A library for controlling and interacting with the [Tello EDU](https://www.ryzerobotics.com/tello-edu) drone using [modern asynchronous Python](https://docs.python.org/3/library/asyncio.html).  All operations are implemented as awaitable coroutines, completed when the drone sends acknowledgment of the command message.


``` python
import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())
```

See the [examples](examples) directory for more usage example scripts.

Requires Python 3.7+, developed and tested with Python 3.9.4

## Version History

**1.0.0**

Basic drone control
- UDP connection for sending commands and receiving responses (default AP mode only - you must join the drone's own WiFi network)
- take off and land
- rotate clockwise and counter-clockwise
- move up, down, left, right, forward and back

**1.1.0**

Drone state
- listens for and parses UDP state messages (not yet including the mission pad related values)
- access via the read only `state` object attribute, or via shortcuts like `height`, `temperature` etc
- constructor takes an optional `on_state` callback argument for notification of new state
- or use the asynchronous generator `state_stream` for an infinite stream of updates  

**1.2.0**

Advanced drone control
- flips
- go/curve to relative position
- emergency stop

Video
- start/stop video stream
- video url

Error handling
- handles error command responses from drone

**1.3.0**

Complete SDK
- mission pads
- wifi
- remote control

Video
- raw video frame data via callback or async generator

Error handling
- detects command/response mismatch

**1.3.1**
- Documentation

## Roadmap

Coming soon...

- Python 3.6 support 
