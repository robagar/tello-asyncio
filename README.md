# tello-asyncio

A library for controlling and interacting with the [Tello EDU](https://www.ryzerobotics.com/tello-edu) drone using [modern asynchronous Python](https://docs.python.org/3/library/asyncio.html).  All operations are implemented as awaitable coroutines, completed when the drone sends acknowledgment of the command message.

Package [tello-asyncio](https://pypi.org/project/tello-asyncio/) on PyPi. 

``` bash
$ pip3 install tello-asyncio
```

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

Requires Python 3.6+. Developed and tested with Python 3.9.4 in Mac OS and 3.6.9 in Ubuntu 18.04 on a [Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit).  The *tello_asyncio* package has no other dependencies (and never will have any), but some examples need other things to be installed to work.

Full documentation is available on [Read the docs](https://tello-asyncio.readthedocs.io/en/latest/)

## Tello SDK Support

* [Tello SDK 2.0](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf) (Tello EDU) - complete support
* [Tello SDK 3.0](https://dl.djicdn.com/downloads/RoboMaster+TT/Tello_SDK_3.0_User_Guide_en.pdf) (RoboMaster TT) - complete support, but `EXT` commands for controlling LEDs etc must be formatted by the user

## A Note on Awaiting

The Tello SDK command/response model is a natural fit for the asynchronous python [awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables) idea, but the drone will get confused if commands are sent before it's had a chance to respond. Each command should be *awaited* before sending the next.

It works best sequentially like this... 

``` python
await drone.takeoff()
await drone.land()
```
...but **not** concurrently (which will not work as expected)
``` python 
await asyncio.gather(
    drone.takeoff(), 
    drone.land()
)
```

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

**1.3.2**

- Documentation on [Read the docs](https://tello-asyncio.readthedocs.io/en/latest/)

**1.4.0**

- Video frame data reassembled properly from UDP packet chunks 
- Working video frame decoding example

**1.4.1**

- Video in OpenCV example

**1.5.0**

- Python 3.6 support 

**1.6.0**

- Drone instance passed to state and video callbacks
- Wait for WiFi network (Linux only)

**2.0.0**

- Tello SDK 3.0 support

**2.1.0**

- Wait for Wifi network implemented for macOS as well as Linux
- Mission pad fixes & example improvement (thanks @jsolderitsch!)

**2.1.1**

- Examples ask the user for the WiFi name prefix


