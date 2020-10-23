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

        moistureSensor = Sensor(self.config, 32, "soil")
        moistureSensor.takeReading()

        voltageSensor = Sensor(self.config, 33, "volt", multiplier=5)
        voltageSensor.takeReading()

        if wifiIsConnected:
            moistureSensor.sendReadings()

        # blinker = BlinkMessage()
        # blinker.genericBlink()

        # sensorReadPin = Pin(33, Pin.IN, None)
        # adc = ADC(sensorReadPin)
        # adc.atten(ADC.ATTN_11DB)

        self.goToSleep()

    def setPins(self):
        print("Setting pins")
        # These pins can't be used as output for the power supply
        # machine.Pin(35, machine.Pin.OUT, None).on()
        # machine.Pin(34, machine.Pin.OUT, None).off()

        # Pin(35, Pin.IN, Pin.PULL_HOLD)
        # Pin(34, Pin.IN, Pin.PULL_HOLD)

        # # These pins are fine to use as the power supply
        # print("==================================")
        # for i in [32, 33, 34, 35]:
        #     print(i)
        #     pin = ADC(Pin(i, Pin.IN, None))
        #     pin.atten(ADC.ATTN_11DB)
        #     print("pin {}: {}".format(i, pin.read()))
        #     Pin(i, Pin.IN, Pin.PULL_HOLD)
        #     Pin(i, Pin.OUT, None)

        Pin(25, Pin.OUT, None).on()
        Pin(26, Pin.OUT, None).off()

        # soil = ADC(Pin(32, Pin.IN, None))
        # soil.atten(ADC.ATTN_11DB)
        # print("soil reading: {}".format(soil.read()))

        # volt = ADC(Pin(33, Pin.IN, None))
        # volt.atten(ADC.ATTN_11DB)
        # reading = volt.read()
        # print("volt reading: {} x5: {}".format(reading, reading * 5))

    def holdPins(self):
        """Hold the pins before sleep to prevent current leakage"""
        print("Holding pins")
        p16 = Pin(self.config.get("ledPin"), Pin.IN, Pin.PULL_HOLD)

        # These pins can't be used as output for the power supply
        # machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_HOLD)
        # machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_HOLD)

        # These pins are fine to use as the power supply
        Pin(25, Pin.IN, Pin.PULL_HOLD)
        Pin(26, Pin.IN, Pin.PULL_HOLD)

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


if __name__ == "__main__":

    from config import Config

    config = Config()

    masterActions = MasterActions(config)
    masterActions.run()