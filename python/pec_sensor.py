import protocol

class PECSensor:
    def __init__(self, dispatch):
        self.protocol = protocol.Protocol()
        self.dispatch = dispatch


    def test(self, value, on_done):
        def handle(lines):
            data = self._parse(lines)
            self.dispatch(lambda: on_done(data))
        return self.protocol.send_command(f"MEASURE", handle)

    def ping(self):
        def handle(lines):
            data = self._parse_ping(lines)
            self.dispatch(lambda: print(data))
        return self.protocol.send_command(f"PING", handle)

    # just a test function for now
    def _parse_ping(self, lines):
        if len(lines) == 0: return "ping failed"
        ping = lines[0]
        return ping

    # just a test function for now
    def _parse(self, lines):
        return lines

