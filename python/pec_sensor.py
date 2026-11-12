import protocol

class PECSensor:
    def __init__(self, dispatch):
        self.protocol = protocol.Protocol()
        self.dispatch = dispatch


    def test(self, value, on_done):
        def handle(lines):
            data = self._parse(lines)
            self.dispatch(lambda: on_done(data))
        return self.protocol.send_command(f"MEASURE", {value}, handle)


    # just a test function for now
    def _parse(self, lines):
        return lines

sensor = PECSensor()
print(sensor.test)
