import asyncio
from collections import deque

from .types import Direction, MissionPadDetection
from .state import TelloStateListener
from .video import TelloVideoListener, VIDEO_URL

DEFAULT_DRONE_HOST = '192.168.10.1'

CONTROL_UDP_PORT = 8889
STATE_UDP_PORT = 8890

DEFAULT_RESPONSE_TIMEOUT = 10
LONG_RESPONSE_TIMEOUT = 60

class Tello:
    '''
    For ayncio-based interaction with the Tello EDU drone.

    :param drone_host: str, Drone IP address, defaults to '192.168.10.1'
    :param on_state: callback, Called when state data is received from the drone, defaults `None`
    :param on_video_frame: callback, Called when video frame data is received from the drone, defaults `None`
    '''

    _protocol = None
    _transport = None

    _state = None
    _video = None
    _flying = False

    class Error(Exception):
        '''
        Exception thrown if anything goes wrong controlling the drone.
        '''
        pass

    class Protocol:
        '''
        UDP protocol for drone control using the Tello SDK.
        The basic flow from the user's point of view is

           SEND command -> drone does something -> RECEIVE response

        Messages are plain ASCII text, eg command "forward 10" -> response "ok"
        '''
        def connection_made(self, transport):
            self.pending = deque()

        def datagram_received(self, data, addr):
            try:
                message = data.decode('ascii')
            except UnicodeDecodeError as e:
                raise Tello.Error(f'DECODE ERROR {e} (data: {data})')
                
            print('RECEIVED', message)
            try:
                sent_message, response, response_parser = self.pending.popleft()
                if response_parser:
                    result = response_parser(message)
                else:    
                    if message == 'ok':
                        result = None
                    else:
                        response.set_exception(Tello.Error(message))
                        return
                response.set_result((sent_message, result))

            except IndexError:
                raise Tello.Error('NOT WAITING FOR RESPONSE')
            except asyncio.exceptions.InvalidStateError:
                pass

        def error_received(self, error):
            raise Tello.Error(f'PROTOCOL ERROR {error}')

        def connection_lost(self, error):
            # print('CONNECTION LOST', error)
            for m, response, rp in self.pending:
                response.cancel()
            self.pending.clear()

    def __init__(self, drone_host=DEFAULT_DRONE_HOST, on_state=None, on_video_frame=None):
        '''
        Constructor
        '''
        self._drone_host = drone_host
        self._on_state_callback = on_state
        self._on_video_frame_callback = on_video_frame
        self._loop = asyncio.get_event_loop()

    async def connect(self):
        '''
        Opens the UDP connection to the drone and puts it in SDK mode.
        :async:
        '''
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

        # tell drone to be in SDK mode
        await self.send('command')

    async def disconnect(self):
        '''
        Closes the UDP connection.
        :async:
        '''
        if self._transport and not self._transport.is_closing():
            print(f'DISCONNECT {self._drone_host}')

            self._transport.close()
            await self._state_listener.disconnect()
            if self._video:
                await self._video.disconnect()

    @property
    async def serial_number(self):
        '''
        The unique drone serial number.
        :async:
        '''
        return await self.send('sn?', response_parser=lambda m: m)

    @property
    async def sdk_version(self):
        '''
        The Tello SDK version.
        :async:
        '''
        return await self.send('sdk?', response_parser=lambda m: m)

    @property
    async def query_battery(self):
        '''

        :async:
        '''
        return await self.send('battery?', response_parser=lambda m: int(m))

    @property
    async def query_motor_time(self):
        '''

        :async:
        '''
        return await self.send('time?', response_parser=lambda m: int(m))

    async def emergency_stop(self):
        '''

        :async:
        '''
        await self.send('emergency')

    async def takeoff(self):
        '''

        :async:
        '''
        self._flying = True
        await self.send('takeoff')

    async def land(self):
        '''

        :async:
        '''
        await self.send('land')
        self._flying = False

    @property
    def flying(self):
        '''

        '''
        return self._flying

    @property
    async def speed(self):
        '''

        :async:
        '''
        return self.send('speed?', response_parser=lambda m: int(m))

    async def set_speed(speed):
        '''

        :async:
        '''
        await self.send(f'speed {speed}')

    async def stop(self):
        '''

        :async:
        '''
         await self.send('stop')

    async def turn_clockwise(self, degrees):
        '''

        :async:
        '''
        await self.send(f'cw {degrees}')    

    async def turn_counterclockwise(self, degrees):
        '''

        :async:
        '''
        await self.send(f'ccw {degrees}')

    async def move(self, direction, distance):
        '''

        :async:
        '''
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
        '''

        :async:
        '''
        await self.send(f'up {distance}')

    async def move_down(self, distance):
        '''

        :async:
        '''
        await self.send(f'down {distance}')

    async def move_left(self, distance):
        '''

        :async:
        '''
        await self.send(f'left {distance}')

    async def move_right(self, distance):
        '''

        :async:
        '''
        await self.send(f'right {distance}')

    async def move_forward(self, distance):
        '''

        :async:
        '''
        await self.send(f'forward {distance}')

    async def move_back(self, distance):
        '''

        :async:
        '''
        await self.send(f'back {distance}')

    async def flip(self, direction):
        '''

        :async:
        '''
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
        '''

        :async:
        '''
        await self.send('flip l')

    async def flip_right(self):
        '''

        :async:
        '''
        await self.send('flip r')

    async def flip_forward(self):
        '''

        :async:
        '''
        await self.send('flip f')

    async def flip_back(self):
        '''

        :async:
        '''
        await self.send('flip b')

    async def go_to(self, relative_position, speed, mission_pad=None):
        '''

        :async:
        '''
        p = relative_position
        command = f'go {p.x} {p.y} {p.z} {speed}'
        if mission_pad:
            command += f' m{mission_pad}'
        await self.send(command, timeout=LONG_RESPONSE_TIMEOUT)

    async def curve_to(self, via_relative_position, relative_position, speed, mission_pad=None):
        '''

        :async:
        '''
        p = relative_position
        v = via_relative_position
        command = f'curve {v.x} {v.y} {v.z} {p.x} {p.y} {p.z} {speed}'
        if mission_pad:
            command += f' m{mission_pad}'
        await self.send(command, timeout=LONG_RESPONSE_TIMEOUT)

    async def enable_mission_pads(self):
        '''

        :async:
        '''
        await self.send('mon')

    async def disable_mission_pads(self):
        '''

        :async:
        '''
        await self.send('moff')

    async def set_mission_pad_detection(self, mission_pad_detection):
        '''

        :async:
        '''
        await self.send(f'mdirection {mission_pad_detection.value}')

    async def jump(self, relative_position, speed, yaw, from_mission_pad, to_mission_pad):
        '''

        :async:
        '''
        p = relative_position
        command = f'jump {p.x} {p.y} {p.z} {speed} {yaw} m{from_mission_pad} m{to_mission_pad}'
        await self.send(command)

    async def remote_control(self, left_right, forward_back, up_down, yaw):
        '''

        :async:
        '''
        await self.send(f'rc {left_right} {forward_back} {up_down} {yaw}')

    async def set_wifi_credentials(self, ssid, password):
        '''

        :async:
        '''
        await self.send(f'wifi {ssid} {password}')

    async def connect_to_wifi(self, ssid, password):
        '''

        :async:
        '''
        await self.send(f'ap {ssid} {password}')

    @property
    async def wifi_signal_to_noise_ratio(self):
        '''

        :async:
        '''
        return self.send('wifi?', response_parser=lambda m: int(m))

    async def send(self, message, timeout=DEFAULT_RESPONSE_TIMEOUT, response_parser=None):
        '''

        :async:
        '''
        if not self._transport.is_closing():
            print(f'SEND {message}')
            response = self._loop.create_future()
            self._protocol.pending.append((message, response, response_parser))
            self._transport.sendto(message.encode())
            try:
                response_message, result = await asyncio.wait_for(response, timeout=timeout)
                if response_message != message:
                    raise Tello.Error('RESPONSE WRONG MESSAGE "{response_message}", expected "{message}" (UDP packet loss detected)')
                return result
            except asyncio.TimeoutError:
                print(f'TIMEOUT {message}')
                await self._abort()
            except Tello.Error as error:
                print(f'[{message}] ERROR {error}')
                await self._abort()

    async def _abort(self):
        '''

        :async:
        '''
        if self._flying:
            await self.land()
        await self.disconnect()

    @property
    def state(self):
        '''

        :async:
        '''
        return self._state

    @property
    async def state_stream(self):
        '''

        :async:
        '''
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
        '''
        '''
        if self._state:
            return getattr(self._state, name) 

    @property
    def video_url(self):
        '''
        '''
        return VIDEO_URL

    async def start_video(self, on_frame=None):
        '''

        :async:
        '''
        await self.send('streamon')
        if on_frame:
            await self.connect_video(on_frame)

    async def stop_video(self):
        '''

        :async:
        '''
        await self.send('streamoff')

    async def connect_video(self, on_frame=None):
        '''

        :async:
        '''
        if on_frame:
            self._on_video_frame_callback = on_frame
        self._video = TelloVideoListener()
        self._video_frame_event = asyncio.Event()
        await self._video.connect(self._loop, self._on_video_frame)

    def _on_video_frame(self, frame):
        if self._on_video_frame_callback:
            self._on_video_frame_callback(frame)
        self._video_frame = frame
        self._video_frame_event.set()
        self._video_frame_event.clear()

    _video_frame = None
    @property
    def video_frame(self):
        '''
        '''
        return self._video_frame

    @property
    async def video_stream(self):
        '''

        :async:
        '''
        while True:
            await self._video_frame_event.wait()
            yield self._video_frame

