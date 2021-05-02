import asyncio
from .protocol import TelloProtocol
from .state import TelloStateListener

DEFAULT_DRONE_HOST = '192.168.10.1'

CONTROL_UDP_PORT = 8889
STATE_UDP_PORT = 8890

RESPONSE_TIMEOUT = 10


class Tello:
    '''
    For ayncio-based interaction with the Tello EDU drone.
    '''

    _protocol = None
    _transport = None

    _state = None

    def __init__(self, drone_host=DEFAULT_DRONE_HOST, on_state=None):
        self._drone_host = drone_host
        self._on_state_callback = on_state
        self._loop = asyncio.get_event_loop()

    async def connect(self):
        print(f'CONNECT {self._drone_host}')

        transport, protocol = await self._loop.create_datagram_endpoint(
            TelloProtocol, 
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

    async def takeoff(self):
        await self.send('takeoff')

    async def land(self):
        await self.send('land')

    async def turn_clockwise(self, degrees):
        await self.send(f'cw {degrees}')    

    async def turn_counterclockwise(self, degrees):
        await self.send(f'ccw {degrees}')    

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

    async def send(self, message):
        if not self._transport.is_closing():
            print(f'SEND {message}')
            self._protocol.command_ok = self._loop.create_future()
            self._transport.sendto(message.encode())
            try:
                await asyncio.wait_for(self._protocol.command_ok, timeout=RESPONSE_TIMEOUT)
            except asyncio.TimeoutError:
                print(f'TIMEOUT {message}, disconnecting')
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

