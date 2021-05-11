VIDEO_UDP_PORT = 11111
VIDEO_URL = f'udp://0.0.0.0:{VIDEO_UDP_PORT}'

VIDEO_WIDTH = 960
VIDEO_HEIGHT = 720

MAX_CHUNK_SIZE = 1460

class TelloVideoListener:
    '''
    Connects to the drone's video data stream and reassembles h.264 encoded 
    frames from UDP packet chunks before passing them on.
    '''

    _transport = None

    class Protocol:
        def connection_made(self, transport):
            self._chunks = []

        def datagram_received(self, data, addr):
            self._chunks.append(data)
            if len(data) != MAX_CHUNK_SIZE:
                frame = b''.join(self._chunks)
                self._chunks = [] 
                self.on_frame_received(frame)

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