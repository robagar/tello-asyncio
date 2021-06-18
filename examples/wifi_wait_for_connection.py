#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)

        print('...ok, can connecting to drone now')
        await drone.connect()

        snr = await drone.wifi_signal_to_noise_ratio
        print(f'WiFi signal to noise ratio: {snr}%')
    finally:
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())