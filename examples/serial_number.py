#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.connect()
        serial_number = await drone.serial_number
        print(f'serial number: {serial_number}')
    finally:
        await drone.disconnect()

asyncio.run(main())