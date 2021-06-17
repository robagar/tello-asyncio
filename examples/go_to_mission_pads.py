#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector

async def main():
    drone = Tello()

    def output_state():
        print(f'mission pad: {drone.mission_pad}, position: {drone.mission_pad_position}')

    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        await drone.enable_mission_pads()
        await drone.takeoff()
        output_state()
        await drone.go_to(relative_position=Vector(0, 0, 120), speed=50, mission_pad=1)
        output_state()
        await drone.go_to(relative_position=Vector(150, 0, 120), speed=50, mission_pad=1)
        output_state()
        await drone.go_to(relative_position=Vector(0, 0, 120), speed=50, mission_pad=2)
        output_state()
        await drone.go_to(relative_position=Vector(150, 0, 120), speed=50, mission_pad=2)
        output_state()
        await drone.go_to(relative_position=Vector(0, 0, 120), speed=50, mission_pad=3)
        output_state()
        await drone.land()
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())