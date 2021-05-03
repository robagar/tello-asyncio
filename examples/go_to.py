#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.go_to(relative_position=Vector(100, 50, 100), speed=25)
        await drone.go_to(relative_position=Vector(-100, -50, -100), speed=25)
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())