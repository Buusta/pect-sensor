import serial
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo


class Protocol:
    def __init__(self):
        self.available_ports: list[ListPortInfo] = []
        self.serial: serial.Serial | None = None
        self.get_available_ports()

    def get_available_ports(self):
        self.available_ports = []
        for p in list_ports.comports():
            if p.vid != None:
                self.available_ports.append(p)
        return self.available_ports

    def connect(self, vid: int):
        if not self.serial is None and self.serial.is_open:
            self.serial.close()
            self.serial = None

        for p in self.available_ports:
            if p.vid == vid:
                device: str = p.device
                description: str = p.description

                try:
                    self.serial = serial.Serial(device, 115200, timeout=3)
                except:
                    print(f"failed to connect to {vid}")
                    return

                print(f"connected to: {vid}, {device}, {description}")
                return

        print(f"device not found: {vid}")

    def read(self) -> str:
        if self.serial is None or not self.serial.is_open:
            return ""

        try:
            return self.serial.readline().decode("utf-8").strip()
        except serial.SerialException:
            print("Couldn't read from serial device")
            self.serial = None
            return ""

    def write(self, command: str):
        if self.serial is None or not self.serial.is_open:
            return

        self.serial.write((command + "\n").encode("utf-8"))

protocol = Protocol()
protocol.connect(11914)

while True:
    read = protocol.read()
    if read != "":
        print(read)

    protocol.write("yay")
