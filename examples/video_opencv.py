#!/usr/bin/env python3

##############################################################################
#
# A minimal proof of concept of controlling the drone while capturing and
# showing video using OpenCV.
#
# The OpenCV UI must run in the main thread, so the drone control runs in a
# worker thread with its own asyncio event loop.
#
# Please note:
#   - If OpenCV fails to capture any video it gives up without showing the
#     window
#   - The video plays a few seconds behind the live action. This appears to
#     be a limitation of the OpenCV capture.read() / cv2.imshow() approach
#
##############################################################################

import asyncio
from threading import Thread

import cv2  # requires python-opencv

from tello_asyncio import Tello, VIDEO_URL

print("[main thread] START")

##############################################################################
# drone control in worker thread


def fly():
    print("[fly thread] START")

    async def main():
        drone = Tello()
        try:
            await asyncio.sleep(1)
            await drone.wifi_wait_for_network(prompt=True)
            await drone.connect()
            await drone.start_video(connect=False)
            await drone.takeoff()
            await drone.turn_clockwise(360)
            await drone.land()
        finally:
            await drone.stop_video()
            await drone.disconnect()

    # Python 3.7+
    # asyncio.run(main())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

    print("[fly thread] END")


# needed for drone.wifi_wait_for_network() in worker thread in Python < 3.8
asyncio.get_child_watcher()

fly_thread = Thread(target=fly, daemon=True)
fly_thread.start()

##############################################################################
# Video capture and GUI in main thread

print(f"[main thread] OpenCV capturing video from {VIDEO_URL}")
print(
    f"[main thread] Press Ctrl-C or any key with the OpenCV window focussed to exit (the OpenCV window may take some time to close)"
)


capture = None
try:
    capture = cv2.VideoCapture(VIDEO_URL)
    capture.open(VIDEO_URL)

    while True:
        # grab and show video frame in OpenCV window
        grabbed, frame = capture.read()
        if grabbed:
            cv2.imshow("tello-asyncio", frame)

        # process OpenCV events and exit if any key is pressed
        if cv2.waitKey(1) != -1:
            break
except KeyboardInterrupt:
    pass
finally:
    # tidy up
    if capture:
        capture.release()
    cv2.destroyAllWindows()

print("[main thread] END")
