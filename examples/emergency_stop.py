#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.emergency_stop()  # warning! this will make the drone drop like a brick
    finally:
        await drone.disconnect()

asyncio.run(main())