import serial
import time


class Point:
    time: int
    value: int

    def __init__(self, time: int, value: int) -> None:
        self.time = time
        self.value = value

    def __str__(self) -> str:
        return f"self.time = {self.time:<20} self.value = {self.value:<20}"


class Serial_reed(serial.Serial):
    list_serial_read: list[Point] = []

    def __init__(self, port: str = None, baudrate: int = 9600):
        super().__init__(port, baudrate)
        self.reset_input_buffer()  # Очистка кеша буфера

    def read_serial(self):
        serial_bytes = self.readline()
        decoded_serial_bytes = serial_bytes[0:len(serial_bytes) - 2].decode("utf-8")

        decoded_serial_bytes_str = decoded_serial_bytes.split(";")

        point = Point(int(decoded_serial_bytes_str[0]), int(decoded_serial_bytes_str[1]))

        self.list_serial_read.append(point)


port = '/dev/cu.usbmodem2301'
baudrate = 115200

ser = Serial_reed(port, baudrate)  # Подключение к порту

time_start = time.monotonic()

while True:
    ser.read_serial()

    if (time.monotonic() - time_start >= 20):  # 5 Секунд работы
        break

print(*ser.list_serial_read, sep="\n")
from scipy.signal import find_peaks

from biosppy.signals import ecg

ecgOut = ecg.ecg(signal=ser.list_serial_read, sampling_rate=1000., show=False)

rPeaks = ecgOut[2]
rrTachogram = []
prevPeak = rPeaks[0]
for peak in rPeaks[1:(len(rPeaks))]:
    rrTachogram.append(peak - prevPeak)
    prevPeak = peak

templatesForCorrCoef = ecgOut[4]
templates = templatesForCorrCoef
medianTemplate = [x / len(templates) for x in [sum(x) for x in zip(*templates)]]

print(len(medianTemplate))