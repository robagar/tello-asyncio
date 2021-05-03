#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Direction

def on_drone_state(state):
    print(f'acceleration: {state.acceleration}, velocity: {state.velocity}')


async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.connect()
        await drone.takeoff()
        for direction in [Direction.LEFT, Direction.RIGHT, Direction.FORWARD, Direction.BACK]:
            await drone.flip(direction) 
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())