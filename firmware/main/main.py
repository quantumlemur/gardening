from machine import ADC, deepsleep, Pin, RTC, Signal
from network import WLAN, STA_IF
from time import sleep, time
from esp32 import Partition
from ujson import loads

# file imports
from sensors import sendReadings, Sensors
from utilities import now

pinModes = {
    "OUT": Pin.OUT,
    "IN": Pin.IN,
    "OPEN_DRAIN": Pin.OPEN_DRAIN,
}
pinPulls = {
    "UP": Pin.PULL_UP,
    "DOWN": Pin.PULL_DOWN,
    "HOLD": Pin.PULL_HOLD,
    "NONE": None,
}


class MasterActions:
    def __init__(self, config):
        self.config = config
        self.setPins()

    def run(self):
        wifiIsConnected = WLAN(STA_IF).isconnected()

        sensorList = loads(self.config.get("SENSORS"))

        for s in sensorList:
            print("Defining sensor on pin {}".format(s["pin"]))
            sensor = Sensors(self.config, s["pin"], s["sensorName"], s["multiplier"])
            sensor.takeReading()

        if wifiIsConnected:
            sendReadings(self.config)
            # import test

        # blinker = BlinkMessage()
        # blinker.genericBlink()

        # sensorReadPin = Pin(33, Pin.IN, None)
        # adc = ADC(sensorReadPin)
        # adc.atten(ADC.ATTN_11DB)

        self.goToSleep()

    def setPins(self):
        print("Setting pins")

        print(self.config.get("PIN_SETTINGS"))
        pinSettings = loads(self.config.get("PIN_SETTINGS"))
        for p in pinSettings:
            pin = Pin(p["pin"], mode=pinModes[p["mode"]], pull=pinPulls[p["pull"]])

            if p["mode"] == "OUT":
                pin.value(p["value"])

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

        # Pin(25, Pin.OUT, None).on()
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

        # First get the misc pins set in the config
        pinSettings = loads(self.config.get("PIN_SETTINGS"))
        pins = [p["pin"] for p in pinSettings]

        # Then add the LED pins
        for c in ["BOARD_LED_PIN", "R_LED_PIN", "G_LED_PIN", "B_LED_PIN"]:
            pin = self.config.get(c)
            if pin and pin > 0:
                pins.append(pin)

        # Then hold all the collected pins
        for pin in pins:
            print("Holding pin {}".format(pin))
            Pin(pin, mode=Pin.IN, pull=Pin.PULL_HOLD)

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

    from boot import config

    config = config.Config()

    masterActions = MasterActions(config)
    masterActions.run()
