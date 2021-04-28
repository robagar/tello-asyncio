

class TelloState:
    class Protocol:
        def connection_made(self, transport):
            print('[state] CONNECTION MADE')

        def datagram_received(self, data, addr):
            message = data.decode('ascii')
            print('[state] RECEIVED', message)

        def error_received(self, exc):
            print('[state] ERROR', exc)

        def connection_lost(self, exc):
            print('[state] CONNECTION LOST', exc)

    def __init__(self, local_port):
        self._local_port = local_port

    async def connect(self, loop):
        transport, protocol = await loop.create_datagram_endpoint(
            TelloState.Protocol, 
            local_addr=("0.0.0.0", self._local_port)
        )

        self._transport = transport
        self._protocol = protocol        