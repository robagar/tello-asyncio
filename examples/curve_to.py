#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.takeoff()
        await drone.curve_to(
            via_relative_position=Vector(75, 0, 75),
            relative_position=Vector(0, 0, 150),
            speed=25,
        )
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
