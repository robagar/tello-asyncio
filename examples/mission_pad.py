#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, MissionPadDetection

def on_drone_state(drone, state):
    print(f'mission pad: {state.mission_pad_id}, position: {state.mission_pad_position}')

async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.enable_mission_pads()
        await drone.set_mission_pad_detection(MissionPadDetection.DOWN)
        await drone.move_forward(100)
        await drone.move_back(100)
        await drone.land()
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())