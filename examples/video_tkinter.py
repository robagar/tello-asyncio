#!/usr/bin/env python3

import asyncio
from threading import Thread
import tkinter  # requires python-tk
import av       # requires pyav
from PIL import Image, ImageTk  # requires Pillow

from tello_asyncio import Tello, VIDEO_WIDTH, VIDEO_HEIGHT

frame_image = None

##############################################################################
# drone control in worker thread


def fly():
    codec = av.CodecContext.create('h264', 'r')

    def on_video_frame(drone, buf):
        global frame_image
        try:
            packets = codec.parse(buf)
            for packet in packets:
                frames = codec.decode(packet)
                for frame in frames:
                    frame_image = frame.to_image()
        except Exception as e:
            print(e)

    async def main():
        drone = Tello()
        try:
            await drone.wifi_wait_for_network(prompt=False)
            await drone.connect()
            await drone.start_video(on_video_frame)
            await drone.takeoff()
            await drone.turn_clockwise(360)
            await drone.land()
        finally:
            await drone.stop_video()
            await drone.disconnect()

    asyncio.run(main())


# needed for drone.wifi_wait_for_network() in worker thread in Python < 3.8
asyncio.get_child_watcher()

fly_thread = Thread(target=fly, daemon=True)
fly_thread.start()

##############################################################################
# GUI in main thread

tk = tkinter.Tk()
tk.title("tello-asyncio video")

window = tkinter.Frame(tk)

canvas = tkinter.Canvas(tk, width=VIDEO_WIDTH, height=VIDEO_HEIGHT, bg="blue")
canvas.pack()

photo_image = None
canvas_image = None
last_frame_image = None


def show_frame():
    global photo_image, canvas_image, last_frame_image
    if frame_image is not last_frame_image:
        photo_image = ImageTk.PhotoImage(frame_image)
        if canvas_image:
            canvas.delete(canvas_image)
        canvas_image = canvas.create_image(0, 0, anchor="nw", image=photo_image)
        last_frame_image = frame_image
    schedule_show_frame()


SHOW_FRAME_INTERVAL_MS = 40  # ~25 fps


def schedule_show_frame():
    tk.after(SHOW_FRAME_INTERVAL_MS, show_frame)


schedule_show_frame()
tk.mainloop()
