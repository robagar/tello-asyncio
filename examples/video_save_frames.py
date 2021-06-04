#!/usr/bin/env python3
from pathlib import Path
import asyncio
import h264decoder # see https://github.com/DaWelter/h264decoder for installation instructions
from PIL import Image # requires Pillow

from tello_asyncio import Tello

Path("video_save_frames").mkdir(exist_ok=True)

i = 1
decoder = h264decoder.H264Decoder()
def on_video_frame(drone, frame):
    global i

    try:
        (frame_info, num_bytes) = decoder.decode_frame(frame)
        (frame_data, width, height, row_size) = frame_info
        if width and height:
            image = Image.frombytes('RGB', (width,height), frame_data)
            file_path = f'video_save_frames/frame-{i}.jpg'
            image.save(file_path)
            i += 1
    except Exception as e:
        print(e)

async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network()
        await drone.connect()
        await drone.start_video(on_video_frame)
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()

# Python 3.7+
#asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
