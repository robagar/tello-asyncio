#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.start_video()
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()

asyncio.run(main())