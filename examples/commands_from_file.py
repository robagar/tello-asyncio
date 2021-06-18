#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def is_command(s):
    s = s.strip()
    return s and not s.startswith('#')

with open('commands.txt', 'r') as f:
    commands = [l.strip() for l in f if is_command(l)]  

async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        for i in commands:
            await drone.send(i)
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())