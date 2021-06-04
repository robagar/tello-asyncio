#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        await drone.emergency_stop()  # warning! this will make the drone drop like a brick
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())