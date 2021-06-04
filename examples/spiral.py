#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello, Vector



STEPS = 4
DISTANCE_STEP = 20

async def main():
    drone = Tello()

    async def half_spiral(distance):
        await drone.move_forward(distance)
        await drone.turn_clockwise(90)
        await drone.move_forward(distance)
        await drone.turn_clockwise(90)

    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        await drone.takeoff()
        
        for i in range(2, STEPS+1, 1):
            await half_spiral(i * DISTANCE_STEP)

        for i in range(STEPS, 1, -1):
            await half_spiral(i * DISTANCE_STEP)
   
        await drone.land()
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())