#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.takeoff()
        await drone.go_to(relative_position=Vector(100, 50, 100), speed=25)
        await drone.go_to(relative_position=Vector(-100, -50, -100), speed=25)
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
