import protocol

class PECSensor:
    def __init__(self):
        self.test = "test"
        self.protocol = protocol.Protocol()

sensor = PECSensor()
print(sensor.test)
