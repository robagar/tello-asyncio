#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def on_drone_state(drone, state):
    print(state.raw)

async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())