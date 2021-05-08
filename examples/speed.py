#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()

        for i in range(3):
            await drone.speed = 10 * i
            speed = await drone.speed
            print(f'speed: {speed}') 

        await drone.stop()
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())