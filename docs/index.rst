
tello-asyncio
=============

A library for controlling and interacting with the `Tello EDU <https://www.ryzerobotics.com/tello-edu>`_ drone using `modern asynchronous Python <https://docs.python.org/3/library/asyncio.html>`_.  All operations are implemented as awaitable coroutines, completed when the drone sends acknowledgment of the command message.


.. code-block:: python

    import asyncio
    from tello_asyncio import Tello

    async def main():
        drone = Tello()
        try:
            await drone.connect()
            await drone.takeoff()
            await drone.turn_clockwise(360)
            await drone.land()
        finally:
            await drone.disconnect()

    asyncio.run(main())

Requires Python 3.7+, developed and tested with Python 3.9.4


.. toctree::
   :maxdepth: 3

   modules
   examples

