#!/usr/bin/env python3

# NB requires SDK 3+

import asyncio
from tello_asyncio import Tello


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.motor_on()
        await asyncio.sleep(10)
        await drone.motor_off()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
