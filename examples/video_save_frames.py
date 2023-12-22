#!/usr/bin/env python3
from pathlib import Path
import asyncio
import av              # requires pyav
from PIL import Image  # requires Pillow

from tello_asyncio import Tello

Path("video_save_frames").mkdir(exist_ok=True)

codec = av.CodecContext.create('h264', 'r')
i = 1


def on_video_frame(drone, buf):
    global i

    try:
        packets = codec.parse(buf)
        for packet in packets:
            frames = codec.decode(packet)
            for frame in frames:
                image = frame.to_image()
                file_path = f"video_save_frames/frame-{i}.jpg"
                image.save(file_path)
                i += 1
    except Exception as e:
        print(e)


async def main():
    drone = Tello()
    try:
        await drone.wifi_wait_for_network(prompt=True)
        await drone.connect()
        await drone.start_video(on_video_frame)
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()
    finally:
        await drone.stop_video()
        await drone.disconnect()


# Python 3.7+
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
