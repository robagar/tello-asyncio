#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.takeoff()

        for i in range(1, 3):
            await drone.set_speed(10 * i)
            speed = await drone.speed
            print(f"speed: {speed}")

        await drone.stop()
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
