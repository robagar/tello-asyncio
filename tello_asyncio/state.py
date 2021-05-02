from collections import namedtuple

TelloState = namedtuple('TelloState', 'roll pitch yaw height barometer battery time_of_flight motor_time')


class TelloStateListener:

    _transport = None

    class Protocol:
        def connection_made(self, transport):
            print('[state] CONNECTION MADE')

        def datagram_received(self, data, addr):
            message = data.decode('ascii')
            # print('[state] RECEIVED', message)
            state = parse_state_message(message)
            self.on_state_received(state)

        def error_received(self, exc):
            print('[state] ERROR', exc)

        def connection_lost(self, exc):
            print('[state] CONNECTION LOST', exc)

    def __init__(self, local_port):
        self._local_port = local_port

    async def connect(self, loop, on_state_received):
        transport, protocol = await loop.create_datagram_endpoint(
            TelloStateListener.Protocol, 
            local_addr=("0.0.0.0", self._local_port)
        )
        self._transport = transport
        protocol.on_state_received = on_state_received

    async def disconnect(self):
        if self._transport:
            self._transport.close()
            self._transport = None


def parse_state_message(message):
    pairs = [p.split(':') for p in message.rstrip(';\r\n').split(';')]
    value_map = { p[0]:p[1] for p in pairs }

    def get_int_value(key):
        try:
            return int(value_map[key])
        except KeyError:
            return None

    def get_float_value(key):
        try:
            return float(value_map[key])
        except KeyError:
            return None

    roll = get_int_value('roll')
    pitch = get_int_value('pitch')
    yaw = get_int_value('yaw')
    height = get_int_value('h')
    barometer = get_float_value('baro')
    battery = get_int_value('bat')
    time_of_flight = get_int_value('tof')
    motor_time = get_int_value('time')

    return TelloState(roll, pitch, yaw, height, barometer, battery, time_of_flight, motor_time)
