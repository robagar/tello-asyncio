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

See the _examples_ directory for more usage example scripts.

Requires Python 3.7+, developed and tested with Python 3.9.4

## Version History

**1.0.0** 
Basic drone control
- UDP connection for sending commands and receiving responses (default AP mode only - you must join the drone's own WiFi network)
- take off and land
- rotate clockwise and counter-clockwise
- move up, dow, left, right, forward and back

## Roadmap

Coming soon...

- More advanced control
- Drone status
- Video capture
- Error handling

