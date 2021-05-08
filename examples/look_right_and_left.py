#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.turn_clockwise(90)
        await drone.turn_counterclockwise(180)
        await drone.turn_clockwise(90)
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())