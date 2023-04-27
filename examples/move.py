#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello


def on_drone_state(drone, state):
    print(f"acceleration: {state.acceleration}, velocity: {state.velocity}")


async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.takeoff()
        await drone.move_up(50)
        await drone.move_down(50)
        await drone.move_left(50)
        await drone.move_right(50)
        await drone.move_forward(50)
        await drone.move_back(50)
        await drone.land()
    finally:
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
