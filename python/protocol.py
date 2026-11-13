import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo
import threading
import time


class Protocol:
    def __init__(self):
        self.available_ports: list[ListPortInfo] = []
        self.serial: serial.Serial | None = None
        self._thread: threading.Thread | None = None
        self._busy = threading.Lock()
        self.get_available_ports()


    def get_available_ports(self):
        self.available_ports = []
        for p in list_ports.comports():
            if p.vid != None:
                self.available_ports.append(p)
        return self.available_ports


    def connect(self, vid: int):
        self.disconnect(False)

        for p in self.available_ports:
            if p.vid == vid:
                device: str = p.device
                description: str = p.description

                try:
                    self.serial = serial.Serial(device, 115200, timeout=0.1)
                except:
                    print(f"failed to connect to {device}, {description}, {vid}")
                    return

                print(f"connected to {device}, {description}, {vid}")
                return

        print(f"device not found: {vid}")


    def disconnect(self, print_status: bool = True):
        if not self.serial is None and self.serial.is_open:
            if not self._thread is None:
                self._thread.join()

            port = self.serial.port
            self.serial.close()
            self.serial = None
            print(f"disconnected {port}")
            


    def send_command(self, command: str, handler: callable, on_error: callable, timeout: float = 1.0) -> bool:
        if self.serial is None or not self.serial.is_open:
            return False

        if not self._busy.acquire(blocking=False):
            return False

        self._thread = threading.Thread(target=self._run, args=(command, handler, on_error, timeout))
        self._thread.start()
    
        return True


    def _run(self, command, handler, on_error, timeout):
        try:
            self.serial.reset_input_buffer()
            self.serial.write((command + "\n").encode())
            while True:
                line = self._read_line(timeout)
                if line is None:
                    on_error("timeout")
                    return
                if line.startswith("ERR"):
                    on_error(line)
                    return
                if handler(line):
                    return
        except serial.SerialException as e:
            on_error(str(e))
        finally:
            self._busy.release()


    def _read_line(self, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            raw = self.serial.readline()          # port timeout stays 0.1
            if raw:
                return raw.decode("utf-8", errors="replace").strip()
        return None  

