from machine import Pin, Signal
from time import sleep


class BlinkMessage():
    led = Signal(16, Pin.OUT, invert=True)

    def genericBlink(self):
        for i in range(20):
            self.led.on()
            sleep(.1)
            self.led.off()
            sleep(.1)
