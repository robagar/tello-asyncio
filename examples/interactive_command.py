#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def on_drone_error(drone, error):
    print(f'ERROR: {error}')

async def main():
    drone = Tello(on_error=on_drone_error)
    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        print('Enter commands for the drone, or "quit" to finish...') 
        while True:
            command = input().strip()
            if command:
                if command == 'quit':
                    break
                else:
                    await drone.send(command)
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())