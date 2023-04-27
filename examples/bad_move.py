#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.takeoff()
        await drone.move_forward(
            1000000
        )  # too far - will result in an "out of range" error response
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
