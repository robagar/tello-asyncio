#!/usr/bin/env python3

import asyncio
from threading import Thread

import cv2  # requires python-opencv 

from tello_asyncio import Tello, VIDEO_URL

##############################################################################
# drone control in worker thread 

def fly():
    async def main():
        drone = Tello()
        try:
            await drone.wifi_wait_for_network(prompt=True)
            await drone.connect()
            await drone.start_video()
            await drone.takeoff()
            await drone.turn_clockwise(360)
            await drone.land()
        finally:
            await drone.stop_video()
            await drone.disconnect()

    asyncio.run(main())

fly_thread = Thread(target=fly, daemon=True)
fly_thread.start()

##############################################################################
# Video capture and GUI in main thread

capture = cv2.VideoCapture(VIDEO_URL)
capture.open(VIDEO_URL)

while True:
    grabbed, frame = capture.read()
    if grabbed:
        cv2.imshow('tello-asyncio', frame)
    if cv2.waitKey(1) != -1:
        break

capture.release()
cv2.destroyAllWindows()
