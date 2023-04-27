#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        serial_number = await drone.serial_number
        print(f"serial number: {serial_number}")
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
