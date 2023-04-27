#!/usr/bin/env python3

# NB requires SDK 3+

import asyncio
from tello_asyncio import Tello


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        print("Throw the drone hozontally to launch within 5 seconds!")
        await drone.throw_fly()
        await asyncio.sleep(10)
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
