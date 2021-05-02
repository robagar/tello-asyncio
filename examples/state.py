#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def on_drone_state(state):
    print(f'height: {state.height}, battery: {state.battery}')

async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.connect()
        await drone.takeoff()
        await drone.land()
    finally:
        await drone.disconnect()

asyncio.run(main())