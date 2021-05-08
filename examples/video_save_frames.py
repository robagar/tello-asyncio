#!/usr/bin/env python3

import asyncio
import h264decoder # from https://github.com/DaWelter/h264decoder
from PIL import Image

from tello_asyncio import Tello

i = 1
decoder = h264decoder.H264Decoder()
def on_video_frame(frame):
    print(f'FRAME {frame}')
    fs = decoder.decode(frame)
    n = len(fs)
    print(f'fs {n}')
    for f in fs:
        (frame_data, width, height, ls) = f # ls?
        image = Image.frombytes('RGB', (width,height), frame_data)
        file_path = f'video_save_frames/frame-{i}.jpg'
        image.save(file_path)
        i += 1


async def main():
    drone = Tello()
    try:
        await drone.connect()
        await drone.start_video(on_video_frame)
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()

asyncio.run(main())