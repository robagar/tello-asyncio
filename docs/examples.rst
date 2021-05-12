Code examples
=============

More code examples can be found in the repository `examples <https://github.com/robagar/tello-asyncio/tree/main/examples>`_ directory.


Take off and land
-----------------

Connect to the drone, take off and land immediately.  You must join the drone's own wifi network first!

.. literalinclude:: ../examples/takeoff_and_land.py
   :language: python 


Flip
----

Do a flip in each direction.

.. literalinclude:: ../examples/flip.py
   :language: python


State
-----

Get details of the drone's movement, battery level and other state.

.. literalinclude:: ../examples/state.py
   :language: python


Go to mission pads
------------------

Fly from one mission pad to another.  The mission pads must be arranged so that the drone should be able to see them. 

.. literalinclude:: ../examples/go_to_mission_pads.py
   :language: python


Video save frames
-----------------

Connect to streaming video, decode and save frames to file as JPEG images.

Please note that this example has a couple of extra dependencies to install before running:

- `h264decoder <https://github.com/DaWelter/h264decoder>`_ for decoding h.264 encoded frames from the drone
- `Pillow <https://pypi.org/project/Pillow/>`_ image library for saving the JPEGs

.. literalinclude:: ../examples/video_save_frames.py
   :language: python


Video in OpenCV
---------------

Display streaming video in an `OpenCV <https://opencv.org/>`_ window.  

The key point is that the OpenCV GUI expects to have full ownership of the main thread with its own event loop, so the drone control asyncio event loop runs separately in a worker thread.

- `python-opencv <https://pypi.org/project/opencv-python/>`_ or similar

.. literalinclude:: ../examples/video_opencv.py
   :language: python
