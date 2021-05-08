#!/usr/bin/env python3

##############################################################################
#
# NB In theory this displays a window showing the video streamed from the 
# but drone this script DOES NOT REALLY WORK! It has worked once for me, but
# with horrendous latency ~10s
#
# python-opencv must be installed
#
########################################################

import cv2  

import asyncio
from tello_asyncio import Tello

async def main():
    drone = Tello()

    async def fly():
        await drone.takeoff()
        await drone.turn_clockwise(360)
        await drone.land()

    async def show_video():
        print(f'[video] START')
        capture = cv2.VideoCapture(drone.video_url)
        capture.open(drone.video_url)
        await drone.start_video()
        while True:
            grabbed, frame = capture.read()
            if grabbed:
                cv2.imshow('tello-asyncio', frame)
            if cv2.waitKey(1) != -1:
                break
            await asyncio.sleep(1/30)
        print(f'[video] ending...')
        capture.release()
        cv2.destroyAllWindows()
        print(f'[video] END')

    try:
        await drone.connect()
        await asyncio.wait([fly(), show_video()])
    finally:
        await drone.disconnect()

asyncio.run(main())