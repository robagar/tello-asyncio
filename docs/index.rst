
tello-asyncio
=============

A library for controlling and interacting with the `Tello EDU <https://www.ryzerobotics.com/tello-edu>`_ drone using `modern asynchronous Python <https://docs.python.org/3/library/asyncio.html>`_.  All operations are implemented as awaitable coroutines, completed when the drone sends acknowledgment of the command message.

Package `tello-asyncio <https://pypi.org/project/tello-asyncio/>`_ on PyPi. 

.. code-block:: bash
    $ pip3 install tello-asyncio

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

Requires Python 3.6+. Developed and tested with Python 3.9.4 in Mac OS and 3.6.9 in Ubuntu 18.04 on a `Jetson Nano <https://developer.nvidia.com/embedded/jetson-nano-developer-kit>`_ .  The *tello_asyncio* package has no other dependencies (and never will have any), but some examples need other things to be installed to work.


.. toctree::
   :maxdepth: 3

   modules
   examples

A Note on Awaiting
------------------

The Tello SDK command/response model is a natural fit for the asynchronous python `awaitable <https://docs.python.org/3/library/asyncio-task.html#awaitables>`_ idea, but the drone will get confused if commands are sent before it's had a chance to respond. Each command should be *awaited* before sending the next.

It works best sequentially like this... 

.. code-block:: python

    await drone.takeoff()
    await drone.land()

\...but **not** concurrently like this (which will not work as expected)

.. code-block:: python

    await asyncio.gather(
        drone.takeoff(), 
        drone.land()

