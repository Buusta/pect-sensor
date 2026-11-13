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
            


    def send_command(self, command: str, value, callback: callable) -> bool:
        if self.serial is None or not self.serial.is_open:
            return False

        if not self._busy.acquire(blocking=False):
            return False

        self.serial.reset_input_buffer()
        self.serial.write((command + "\n").encode())

        print("test")

        self._thread = threading.Thread(target=self._run, args=(callback,))
        self._thread.start()
    
        return True


    def _run(self, callback):
        try:
            lines = self.read_serial(callback)
        finally:
            self._busy.release()
        
        callback(lines)


    def read_serial(self, callback):
        lines = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            raw = self.serial.readline()
            if not raw: continue
            line = raw.decode("utf-8").strip("\n")
            lines.append(line)

        return lines
        

