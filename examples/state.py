#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def on_drone_state(drone, state):
    print(f'height: {state.height}cm, battery: {state.battery}%')
    v = state.velocity
    print(f'velocity x: {v.x}cm/s, y: {v.y}cm/s, z: {v.z}cm/s')

async def main():
    drone = Tello(on_state=on_drone_state)
    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        await drone.takeoff()
        await drone.land()
    finally:
        await drone.disconnect()

    print(f'total flight time: {drone.motor_time}s')
    print(f'temperature: {drone.temperature.low}-{drone.temperature.high}°C')

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())