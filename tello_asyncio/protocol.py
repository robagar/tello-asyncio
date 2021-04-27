
class TelloProtocol:

    command_ok = None

    def connection_made(self, transport):
        print('CONNECTION MADE')
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode('ascii')
        print('RECEIVED', message)
        if message == 'ok' and self.command_ok and not self.command_ok.done():
            self.command_ok.set_result(True)

    def error_received(self, exc):
        print('ERROR', exc)

    def connection_lost(self, exc):
        print('CONNECTION LOST', exc)
        if self.command_ok:
            self.command_ok.cancel()