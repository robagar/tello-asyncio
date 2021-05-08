#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.enable_mission_pads()
        await drone.go_to(relative_position=Vector(0, 0, 100), speed=25, mission_pad=1)
        await drone.go_to(relative_position=Vector(0, 0, 100), speed=25, mission_pad=2)
        await drone.go_to(relative_position=Vector(0, 0, 100), speed=25, mission_pad=3)
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())