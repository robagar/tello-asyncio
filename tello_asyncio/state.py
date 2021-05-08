from .types import Range, Vector, TelloState


class TelloStateListener:

    _transport = None

    class Protocol:
        def connection_made(self, transport):
            pass

        def datagram_received(self, data, addr):
            message = data.decode('ascii')
            # print('[state] RECEIVED', message)
            state = parse_state_message(message)
            self.on_state_received(state)

        def error_received(self, error):
            print('[state] PROTOCOL ERROR', error)

        def connection_lost(self, error):
            # print('[state] CONNECTION LOST', error)
            pass

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


def parse_state_message(raw):
    pairs = [p.split(':') for p in raw.rstrip(';\r\n').split(';')]
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

    def get_int_range(low_key, high_key):
        return Range(get_int_value(low_key), get_int_value(high_key))

    def get_float_vector(x_key, y_key, z_key):
        return Vector(get_float_value(x_key), get_float_value(y_key), get_float_value(z_key))


    roll = get_int_value('roll')
    pitch = get_int_value('pitch')
    yaw = get_int_value('yaw')
    height = get_int_value('h')
    barometer = get_float_value('baro')
    battery = get_int_value('bat')
    time_of_flight = get_int_value('tof')
    motor_time = get_int_value('time')
    temperature = get_int_range('templ', 'temph')
    acceleration = get_float_vector('agx', 'agy', 'agz')
    velocity = get_float_vector('vgx', 'vgy', 'vgz')
    mission_pad = get_int_value('mid')
    mission_pad_position = get_float_vector('x', 'y', 'z')

    return TelloState(raw, roll, pitch, yaw, height, barometer, battery, time_of_flight, motor_time, temperature, acceleration, velocity, mission_pad, mission_pad_position)
