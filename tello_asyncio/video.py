VIDEO_UDP_PORT = 11111
VIDEO_URL = f'udp://0.0.0.0:{VIDEO_UDP_PORT}'


class TelloVideoListener:

    _transport = None

    class Protocol:
        def connection_made(self, transport):
            pass

        def datagram_received(self, data, addr):
            print('[video] RECEIVED')
            self.on_frame_received(data)

        def error_received(self, error):
            print('[video] PROTOCOL ERROR', error)

        def connection_lost(self, error):
            pass

    async def connect(self, loop, on_video_frame_received):
        transport, protocol = await loop.create_datagram_endpoint(
            TelloVideoListener.Protocol, 
            local_addr=("0.0.0.0", VIDEO_UDP_PORT)
        )
        self._transport = transport
        protocol.on_frame_received = on_video_frame_received

    async def disconnect(self):
        if self._transport:
            self._transport.close()
            self._transport = None