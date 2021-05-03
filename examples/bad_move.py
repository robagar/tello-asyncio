#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello


async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.move_forward(1000000) # too far - will result in an "out of range" error response
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())