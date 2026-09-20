from time import sleep

import gpiozero as GPIO

relay_pulse_seconds = 1
MAX_DURATION = 2.0

terminals: dict[str, list[tuple[int, int]]] = {
    # "t1": [(0, 1), (2, 3)],
    # "t1": [(1, 2), (3, 4)],
    # "t2": [(4, 5), (6, 7)],
    "t3": [(8, 9), (10, 11)],
    "t4": [(12, 13), (14, 15)],
    "t5": [(16, 17), (18, 19)],
    "t6": [(20, 21), (22, 23)],
    # "tX": [(24, 25), (24, 25)]
}


class Relay:

    def __init__(self, pins):
        pin_a, pin_b = pins
        self.pin_no_a = pin_a
        self.pin_no_b = pin_b
        self.a = GPIO.DigitalOutputDevice(pin_a, initial_value=False)
        self.b = GPIO.DigitalOutputDevice(pin_b, initial_value=False)
        self.pulse_seconds = relay_pulse_seconds

    def coil_off(self):
        self.a.off()
        # print(f"{self.pin_no_a}, off")
        self.b.off()
        # print(f"{self.pin_no_b}, off")

    def coil_on(self):
        self.a.on()
        self.b.on()

    def zap(self, duration=1):
        self.coil_on()
        sleep(duration)
        self.coil_off()
