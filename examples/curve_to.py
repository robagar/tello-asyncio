#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.curve_to(relative_position=Vector(0, 0, 150), via_relative_position=Vector(75, 0, 75), speed=25)
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())