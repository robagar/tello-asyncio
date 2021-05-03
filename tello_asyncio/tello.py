import asyncio
from collections import deque

from .types import Direction
from .state import TelloStateListener

DEFAULT_DRONE_HOST = '192.168.10.1'

CONTROL_UDP_PORT = 8889
STATE_UDP_PORT = 8890
VIDEO_UDP_PORT = 11111
VIDEO_URL = f'udp://0.0.0.0:{VIDEO_UDP_PORT}'

DEFAULT_RESPONSE_TIMEOUT = 10
LONG_RESPONSE_TIMEOUT = 60

class Tello:
    '''
    For ayncio-based interaction with the Tello EDU drone.
    '''

    _protocol = None
    _transport = None

    _state = None
    _flying = False

    class Error(Exception):
        pass

    class Protocol:
        def connection_made(self, transport):
            self.responses = deque()

        def datagram_received(self, data, addr):
            message = data.decode('ascii')
            print('RECEIVED', message)
            try:
                response = self.responses.popleft()
                if message.startswith('ok'):
                    response.set_result(message)
                else:
                    response.set_exception(Tello.Error(message))
            except IndexError:
                print('(not waiting for a response)')
            except asyncio.exceptions.InvalidStateError:
                pass

        def error_received(self, error):
            print('PROTOCOL ERROR', error)

        def connection_lost(self, error):
            # print('CONNECTION LOST', error)
            for response in self.responses:
                response.cancel()
            self.responses = None

    def __init__(self, drone_host=DEFAULT_DRONE_HOST, on_state=None):
        self._drone_host = drone_host
        self._on_state_callback = on_state
        self._loop = asyncio.get_event_loop()

    async def connect(self):
        print(f'CONNECT {self._drone_host}')

        transport, protocol = await self._loop.create_datagram_endpoint(
            Tello.Protocol, 
            local_addr=("0.0.0.0", CONTROL_UDP_PORT),
            remote_addr=(self._drone_host, CONTROL_UDP_PORT)
        )

        self._transport = transport
        self._protocol = protocol

        self._state_listener = TelloStateListener(local_port=STATE_UDP_PORT)
        await self._state_listener.connect(self._loop, self._on_state_received)
        self._state_event = asyncio.Event()

        await self.send('command')

    async def disconnect(self):
        if self._transport and not self._transport.is_closing():
            print(f'DISCONNECT {self._drone_host}')

            self._transport.close()
            await self._state_listener.disconnect()

    async def emergency_stop(self):
        await self.send('emergency')

    async def takeoff(self):
        self._flying = True
        await self.send('takeoff')

    async def land(self):
        await self.send('land')
        self._flying = False

    @property
    def flying(self):
        return self._flying

    async def stop(self):
         await self.send('stop')

    async def turn_clockwise(self, degrees):
        await self.send(f'cw {degrees}')    

    async def turn_counterclockwise(self, degrees):
        await self.send(f'ccw {degrees}')

    async def move(self, direction, distance):
        if direction == Direction.UP:
            return await self.move_up(distance)    
        if direction == Direction.DOWN:
            return await self.move_down(distance)    
        if direction == Direction.LEFT:
            return await self.move_left(distance)    
        if direction == Direction.RIGHT:
            return await self.move_right(distance)    
        if direction == Direction.FORWARD:
            return await self.move_forward(distance)    
        if direction == Direction.BACK:
            return await self.move_back(distance)
        raise ValueError('invalid move direction')    

    async def move_up(self, distance):
        await self.send(f'up {distance}')

    async def move_down(self, distance):
        await self.send(f'down {distance}')

    async def move_left(self, distance):
        await self.send(f'left {distance}')

    async def move_right(self, distance):
        await self.send(f'right {distance}')

    async def move_forward(self, distance):
        await self.send(f'forward {distance}')

    async def move_back(self, distance):
        await self.send(f'back {distance}')

    async def flip(self, direction):
        if direction == Direction.LEFT:
            return await self.flip_left()    
        if direction == Direction.RIGHT:
            return await self.flip_right()    
        if direction == Direction.FORWARD:
            return await self.flip_forward()    
        if direction == Direction.BACK:
            return await self.flip_back()
        raise ValueError('invalid flip direction')    

    async def flip_left(self):
        await self.send('flip l')

    async def flip_right(self):
        await self.send('flip r')

    async def flip_forward(self):
        await self.send('flip f')

    async def flip_back(self):
        await self.send('flip b')

    async def go_to(self, relative_position, speed):
        p = relative_position
        await self.send(f'go {p.x} {p.y} {p.z} {speed}', timeout=LONG_RESPONSE_TIMEOUT)

    async def curve_to(self, via_relative_position, relative_position, speed):
        p = relative_position
        v = via_relative_position
        await self.send(f'curve {v.x} {v.y} {v.z} {p.x} {p.y} {p.z} {speed}', timeout=LONG_RESPONSE_TIMEOUT)

    async def send(self, message, timeout=DEFAULT_RESPONSE_TIMEOUT):
        if not self._transport.is_closing():
            print(f'SEND {message}')
            response = self._loop.create_future()
            self._protocol.responses.append(response)
            self._transport.sendto(message.encode())
            try:
                await asyncio.wait_for(response, timeout=timeout)
            except asyncio.TimeoutError:
                print(f'TIMEOUT {message}')
                await self._abort()
            except Tello.Error as error:
                print(f'[{message}] ERROR {error}')
                await self._abort()

    async def _abort(self):
        if self._flying:
            await self.land()
        await self.disconnect()

    @property
    def state(self):
        return self._state

    @property
    async def state_stream(self):
        while True:
            await self._state_event.wait()
            yield self._state

    def _on_state_received(self, state):
        if self._on_state_callback:
            self._on_state_callback(state)

        self._state = state
        self._state_event.set()
        self._state_event.clear()

    def __getattr__(self, name):
        if self._state:
            return getattr(self._state, name) 

    @property
    def video_url(self):
        return VIDEO_URL

    async def start_video(self):
        await self.send('streamon')

    async def stop_video(self):
        await self.send('streamoff')

