import serial
import time

ser = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
ser.write(b"MEASURE\n")
end = time.monotonic() + 15
while time.monotonic() < end:
    raw = ser.readline()
    if raw:
        print(raw)

print("finished")