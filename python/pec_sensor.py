import protocol

class PECSensor:
    def __init__(self, dispatch):
        self.protocol = protocol.Protocol()
        self.dispatch = dispatch
        return

    # def test(self, value, on_done):
    #     def handle(lines):
    #         data = self._parse(lines)
    #         self.dispatch(lambda: on_done(data))
    # return self.protocol.send_command(f"MEASURE", handle)

    def ping(self):
        def handler(line):
            self.dispatch(lambda: print(line))
            return True
        def failed(reason):
            self.dispatch(lambda: print(reason))
            return False
        return self.protocol.send_command("PING", handler, failed)

    def measure(self, on_done, on_accepted=print, on_error=print):
        lines = []
        accepted = False

        def failed(reason):
            self.dispatch(lambda: on_error(reason))

        def handler(line):
            nonlocal accepted
            if not accepted:
                if line == "MEASURE OK":
                    accepted = True
                    if on_accepted:
                        self.dispatch(on_accepted)
                elif line.startswith("ERR") or line.startswith("MEASURE ERR"):
                    failed(f"rejected: {line}")
                    return True
                # anything else is stale leftover, ignore it
                return False                    # keep reading
            if line == "MEASURE DONE":             # stage 2: collecting data
                data = self._parse(lines)
                self.dispatch(lambda: on_done(data))
                return True                        # finished
            lines.append(line)
            return False

        return self.protocol.send_command("MEASURE", handler, failed, timeout=60.0)

    def _parse(self, lines):
        rows = []
        for line in lines:
            if line.startswith("#") or line.startswith("time_ms"):
                continue                           # header lines
            t, v = line.split(",")
            rows.append((float(t), float(v)))
        return rows


    # # just a test function for now
    # def _parse_ping(self, lines):
    #     if len(lines) == 0: return "ping failed"
    #     ping = lines[0]
    #     return ping

    # # just a test function for now
    # def _parse(self, lines):
    #     return lines

