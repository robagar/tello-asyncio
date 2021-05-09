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
