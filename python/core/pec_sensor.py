from dataclasses import dataclass
from io import StringIO

import pandas as pd

from core import protocol


@dataclass
class MeasurementSettings:
    def __init__(self, averages=100, pulse_time_ms=15, rest_time_ms=15) -> None:
        self.averages = averages
        self.pulse_time_ms = pulse_time_ms
        self.rest_time_ms = rest_time_ms


class PECSensor:
    def __init__(self, dispatch):
        self.protocol = protocol.Protocol()
        self.dispatch = dispatch
        return

    def ping(self):
        def handler(line):
            self.dispatch(lambda: print(line))
            return True

        def failed(reason):
            self.dispatch(lambda: print(reason))
            return False

        return self.protocol.send_command("PING", handler, failed)

    def measure(
        self, settings: MeasurementSettings, on_done, on_accepted=None, on_error=print
    ):
        lines = []
        accepted = False

        print(settings.averages)

        def failed(reason):
            self.dispatch(lambda: on_error(reason))

        def handler(line):
            nonlocal accepted
            if not accepted:
                if line.startswith("MEASURE OK"):
                    accepted = True
                    if on_accepted:
                        self.dispatch(on_accepted)
                elif line.startswith("ERR") or line.startswith("MEASURE ERR"):
                    failed(f"rejected: {line}")
                    return True
                # anything else is stale leftover, ignore it
                return False  # keep reading
            if line.startswith("MEASURE DONE"):  # stage 2: collecting data
                data = self._parse_mst(lines)
                self.dispatch(lambda: on_done(data))
                return True  # finished
            lines.append(line)
            return False

        print(f"MEASURE {settings.averages}")

        return self.protocol.send_command(
            f"MEASURE {settings.averages}", handler, failed, timeout=60.0
        )

    def _parse_mst(self, lines):
        data = (line for line in lines if not line.startswith("#"))

        return pd.read_csv(StringIO("\n".join(data)))
