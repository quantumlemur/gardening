from machine import ADC, deepsleep, Pin, RTC, Signal
from network import WLAN, STA_IF
from time import sleep, time

# file imports
from sensor import Sensor
from utilities import now


class MasterActions:
    def __init__(self, config):
        self.config = config
        self.setPins()

    def run(self):
        wifiIsConnected = WLAN(STA_IF).isconnected()

        moistureSensor = Sensor()
        moistureSensor.storeReading()

        if wifiIsConnected:
            moistureSensor.sendReadings()

        # blinker = BlinkMessage()
        # blinker.genericBlink()

        # sensorReadPin = Pin(33, Pin.IN, None)
        # adc = ADC(sensorReadPin)
        # adc.atten(ADC.ATTN_11DB)

        # for i in range(50):
        #     print(adc.read())
        #     sleep(.1)

        self.goToSleep()

    def setPins(self):
        print("Setting pins")
        # These pins can't be used as output for the power supply
        # machine.Pin(35, machine.Pin.OUT, None).on()
        # machine.Pin(34, machine.Pin.OUT, None).off()

        # These pins are fine to use as the power supply
        # machine.Pin(25, machine.Pin.OUT, None).on()
        # machine.Pin(26, machine.Pin.OUT, None).off()

        # sensorReadPin = machine.Pin(33, machine.Pin.IN, None)
        # adc = machine.ADC(sensorReadPin)
        # adc.atten(machine.ADC.ATTN_11DB)

    def holdPins(self):
        """Hold the pins before sleep to prevent current leakage"""
        print("Holding pins")
        p16 = machine.Pin(
            self.config.get("ledPin"), machine.Pin.IN, machine.Pin.PULL_HOLD
        )

        # These pins can't be used as output for the power supply
        # machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_HOLD)
        # machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_HOLD)

        # These pins are fine to use as the power supply
        # machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_HOLD)
        # machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_HOLD)

    def goToSleep(self, quickSleep=False):
        sleep_duration = max(
            min(
                self.config.get("SLEEP_DURATION"),
                self.config.get("NEXT_INIT_TIME") - now(),
            ),
            1,
        )
        print(
            "Boot number {} of {}".format(
                self.config.get("bootNum"), self.config.get("MAX_ENTRYS_WITHOUT_INIT")
            )
        )
        print(
            "Boot time {} of {}.  {} seconds until connection".format(
                now(),
                self.config.get("NEXT_INIT_TIME"),
                self.config.get("NEXT_INIT_TIME") - now(),
            )
        )

        # bootNum == 0 signifies to connect to wifi next boot
        if time() == 0:
            print(
                "*** Connecting to wifi next boot, and not sleeping.  Reason: clock at 0"
            )
            sleep_duration = 1
        elif now() + self.config.get("SLEEP_DURATION") >= self.config.get(
            "NEXT_INIT_TIME"
        ):
            print(
                "*** Connecting to wifi next boot.  Reason: next sleep would pass the next connection time."
            )
            self.config.put("bootNum", 0)
        elif self.config.get("bootNum") >= self.config.get("MAX_ENTRYS_WITHOUT_INIT"):
            print(
                "*** Connecting to wifi next boot.  Reason: max num of non-connection boots reached."
            )
            self.config.put("bootNum", 0)
        else:
            print(
                "*** Sleeping and booting like normal, not connecting to wifi next boot."
            )
            self.config.put("bootNum", self.config.get("bootNum") + 1)

        # Turn LED off
        Signal(self.config.get("ledPin"), Pin.OUT, invert=True).off()

        self.holdPins()

        self.config.put("runningWithoutError", True)

        if quickSleep:
            deepsleep(1000)
        else:
            deepsleep(sleep_duration * 1000)