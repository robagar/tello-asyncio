#!/usr/bin/env python3

import asyncio
from tello_asyncio import Tello

def on_video_frame(frame):
    print(f'FRAME {frame}')

async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.start_video(on_video_frame)
        # await drone.takeoff()
        # await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()

asyncio.run(main())