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

    :param drone_host: Drone IP address, defaults to '192.168.10.1'
    :param on_state: Callback called when state data is received from the drone, taking a single :class:`tello_asyncio.types.TelloState` argument.
    :type on_state: Callable, optional
    :param on_video_frame: Called when video frame data is received from the drone, taking a single `bytes` argument containing the raw data from the drone.
    :type on_video_frame: Callable, optional
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

           SEND command → drone does something → RECEIVE response when it's finished

        Messages are plain ASCII text, eg command `forward 10` → response `ok`
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
        Closes all UDP connections to this drone.
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
        '''
        return await self.send('sn?', response_parser=lambda m: m)

    @property
    async def sdk_version(self):
        '''
        The Tello SDK version.
        '''
        return await self.send('sdk?', response_parser=lambda m: m)

    @property
    async def query_battery(self):
        '''
        The battery level as a percentage, requested directly from the drone.
        '''
        return await self.send('battery?', response_parser=lambda m: int(m))

    @property
    async def query_motor_time(self):
        '''
        The active motor time in seconds, requested directly from the drone.
        '''
        return await self.send('time?', response_parser=lambda m: int(m))

    async def emergency_stop(self):
        '''
        Stop all motors immediately.  Warning - this will make the drone drop like a brick.        
        '''
        await self.send('emergency')

    async def takeoff(self):
        '''
        Take off and hover.
        '''
        self._flying = True
        await self.send('takeoff')

    async def land(self):
        '''
        Land and stop motors.
        '''
        await self.send('land')
        self._flying = False

    @property
    def flying(self):
        '''
        True if `takeoff` has been called but `land` has not.
        '''
        return self._flying

    @property
    async def speed(self):
        '''
        The drone speed in cm/s, requested directly from the drone.
        '''
        return self.send('speed?', response_parser=lambda m: int(m))

    async def set_speed(speed):
        '''
        Set the forward speed.

        :param speed: Desired speed, 10-100 cm/s
        '''
        await self.send(f'speed {speed}')

    async def stop(self):
        '''
        Stop and hover in place.
        '''
        await self.send('stop')

    async def turn_clockwise(self, degrees):
        '''
        Turn clockwise.

        :param degrees: int, Angle in degrees 1-360°
        '''
        await self.send(f'cw {degrees}')    

    async def turn_counterclockwise(self, degrees):
        '''
        Turn anticlockwise.

        :param degrees: Angle in degrees 1-360°
        '''
        await self.send(f'ccw {degrees}')

    async def move(self, direction, distance):
        '''
        Move in a straight line in the given direction.

        :param direction: Direction of movement
        :type direction: :class:`tello_asyncio.types.Direction`
        :param distance: The distance to travel, 20-500 cm
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
        Move straight up.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'up {distance}')

    async def move_down(self, distance):
        '''
        Move straight down.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'down {distance}')

    async def move_left(self, distance):
        '''
        Move straight left.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'left {distance}')

    async def move_right(self, distance):
        '''
        Move straight right.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'right {distance}')

    async def move_forward(self, distance):
        '''
        Move straight forwards.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'forward {distance}')

    async def move_back(self, distance):
        '''
        Move straight backwards.

        :param distance: Distance to travel, 20-500 cm
        '''
        await self.send(f'back {distance}')

    async def flip(self, direction):
        '''
        Do a flip in the given direction.

        :param direction: The direction to flip in.
        :type direction: :class:`tello_asyncio.types.Direction` 
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
        Flip left.
        '''
        await self.send('flip l')

    async def flip_right(self):
        '''
        Flip right.
        '''
        await self.send('flip r')

    async def flip_forward(self):
        '''
        Flip forwards.
        '''
        await self.send('flip f')

    async def flip_back(self):
        '''
        Flip backwards.
        '''
        await self.send('flip b')

    async def go_to(self, relative_position, speed, mission_pad=None):
        '''
        Go to the given position, either relative to a mission pad if given, 
        otherwise relative to the current position.

        :param relative_position: Position relative to drone or mission pad
        :type relative_position: :class:`tello_asyncio.types.Vector`
        :param mission_pad: The mission pad ID, 1-8
        :type mission_pad: int, optional 
        '''
        p = relative_position
        command = f'go {p.x} {p.y} {p.z} {speed}'
        if mission_pad:
            command += f' m{mission_pad}'
        await self.send(command, timeout=LONG_RESPONSE_TIMEOUT)

    async def curve_to(self, via_relative_position, relative_position, speed, mission_pad=None):
        '''
        Fly in a curve defined by the two positions, which must lie on a circle with a radius of 50cm - 10m. 

        :param via_relative_position: First position relative to drone or mission pad
        :type via_relative_position: :class:`tello_asyncio.types.Vector`
        :param relative_position: Destination relative to drone or mission pad
        :type relative_position: :class:`tello_asyncio.types.Vector`
        :param speed: The speed to travel at 10-60cm/s
        :type speed: int
        :param mission_pad: The mission pad ID, 1-8
        :type mission_pad: int, optional 
        '''
        p = relative_position
        v = via_relative_position
        command = f'curve {v.x} {v.y} {v.z} {p.x} {p.y} {p.z} {speed}'
        if mission_pad:
            command += f' m{mission_pad}'
        await self.send(command, timeout=LONG_RESPONSE_TIMEOUT)

    async def enable_mission_pads(self):
        '''
        Start attempting to detect mission pads.
        '''
        await self.send('mon')

    async def disable_mission_pads(self):
        '''
        Stop detecting mission pads.
        '''
        await self.send('moff')

    async def set_mission_pad_detection(self, mission_pad_detection):
        '''
        Sets the directions to look for mission pads in - forwards, down or both.
        
        :param mission_pad_detection: Forwards, down or both.
        :param mission_pad_detection: :class:`tello_asyncio.types.MissionPadDetection`
        '''
        await self.send(f'mdirection {mission_pad_detection.value}')

    async def jump(self, relative_position, speed, yaw, from_mission_pad, to_mission_pad):
        '''
        Travel from one mission pad to another.
        
        :param relative_position: Final position relative to the mission pad.
        :type relative_position: :class:`tello_asyncio.types.Vector`
        :param speed: Speed of travel, 10-100 cm/s
        :param yaw: Angle to turn on arrival 0-360°
        '''
        p = relative_position
        command = f'jump {p.x} {p.y} {p.z} {speed} {yaw} m{from_mission_pad} m{to_mission_pad}'
        await self.send(command)

    async def remote_control(self, left_right, forward_back, up_down, yaw):
        '''
        Send remote control commands.

        :param left_right: Desired speed to the left, -100-100 cm/s
        :param forward_back: Desired speed forwards, -100-100 cm/s
        :param up_down: Desired speed up, -100-100 cm/s
        :param yaw: Desired yaw -100-100°/s
        '''
        await self.send(f'rc {left_right} {forward_back} {up_down} {yaw}')

    async def set_wifi_credentials(self, ssid, password):
        '''
        Set credentials for the drone's own WiFi network

        :param ssid: Network name
        :param password: Password
        '''
        await self.send(f'wifi {ssid} {password}')

    async def connect_to_wifi(self, ssid, password):
        '''
        Connect to another WiFi network and reboot.
 
        :param ssid: Network name
        :param password: Password
        '''
        await self.send(f'ap {ssid} {password}')

    @property
    async def wifi_signal_to_noise_ratio(self):
        '''
        The signal-to-noise ratio of the WiFi connection.
        '''
        return self.send('wifi?', response_parser=lambda m: int(m))

    async def send(self, message, timeout=DEFAULT_RESPONSE_TIMEOUT, response_parser=None):
        '''
        Send a command message and wait for response.

        :param message: The command string
        :param timeout: Time to wait in seconds for a response
        :param response_parser: A function that converts the response into a return value. 
        :rtype: `None`, unless `response_parser` is used.
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
        if self._flying:
            await self.land()
        await self.disconnect()

    @property
    def state(self):
        '''
        The current state of the drone, if any.

        :rtype: :class:`tello_asyncio.types.TelloState`
        '''
        return self._state

    @property
    async def state_stream(self):
        '''
        In infinite stream of drone state objects.
        
        :rtype: :class:`tello_asyncio.types.TelloState`
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
        Shortcut to the drone state :class:`tello_asyncio.types.TelloState` properties.
        '''
        if self._state:
            return getattr(self._state, name) 

    @property
    def video_url(self):
        '''
        The URL for video data, if `start_video` has been called.
        '''
        return VIDEO_URL

    async def start_video(self, on_frame=None):
        '''
        Start streaming video data.  Only works in AP mode using the drone's own WiFi.
        '''
        if on_frame:
            await self.connect_video(on_frame)
        await self.send('streamon')
 
    async def stop_video(self):
        '''
        Stop streaming video.
        '''
        await self.send('streamoff')

    async def connect_video(self, on_frame=None):
        '''
        Opens a connection to the `video_url` and listens for the video frame 
        data streamed after `start_video` is called.

        :param on_frame: Callback called when a new frame arrives
        :type on_frame: Callable taking single `bytes` argument
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
        The most recent raw frame data, if any,

        :rtype: `bytes`
        '''
        return self._video_frame

    @property
    async def video_stream(self):
        '''
        Infinite stream of video frame data.
        
        :rtype: `bytes`
        '''
        while True:
            await self._video_frame_event.wait()
            yield self._video_frame

