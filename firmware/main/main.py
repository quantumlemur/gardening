#

# 3rd party imports
from machine import deepsleep, Pin

# Local file imports
from core.config import config
from core.utilities import now, isWifi
from sensors import Sensors

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


@micropython.native
def setPins():
    print("Setting pins...")

    pinSettings = config.get("PIN_SETTINGS")
    if pinSettings:
        for p in pinSettings:
            # print(p)
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
    # Pin(26, Pin.OUT, None).off()

    # soil = ADC(Pin(32, Pin.IN, None))
    # soil.atten(ADC.ATTN_11DB)
    # print("soil reading: {}".format(soil.read()))

    # volt = ADC(Pin(33, Pin.IN, None))
    # volt.atten(ADC.ATTN_11DB)
    # reading = volt.read()
    # print("volt reading: {} x5: {}".format(reading, reading * 5))


@micropython.native
def holdPins():
    """Hold the pins before sleep to prevent current leakage"""
    print("Holding pins...")

    # First get the misc pins set in the config
    pinSettings = config.get("PIN_SETTINGS")
    pins = [p["pin"] for p in pinSettings if pinSettings]

    # Then add the LED pins
    for c in ["BOARD_LED_PIN", "R_LED_PIN", "G_LED_PIN", "B_LED_PIN"]:
        pin = config.get(c)
        if pin and pin > 0:
            pins.append(pin)

    # Then hold all the collected pins
    for pin in pins:
        # print("Holding pin {}".format(pin))
        Pin(pin, mode=Pin.IN, pull=Pin.PULL_HOLD)


@micropython.native
def goToSleep(quickSleep=False):
    sleep_duration = max(
        min(
            config.get("SLEEP_DURATION"),
            config.get("NEXT_INIT_TIME") - now(),
            60 * 60 * 24,  # hardcoded 24-hour max sleep
        ),
        1,
    )

    # Turn LED off
    # Signal(config.get("ledPin"), Pin.OUT, invert=True).off()

    holdPins()

    config.put("runningWithoutError", True)

    # close the database
    config.close()

    if quickSleep:
        deepsleep(1000)
    else:
        deepsleep(sleep_duration * 1000)


if __name__ == "__main__":
    setPins()

    with Sensors() as sensors:
        sensors.readSensors()

        if isWifi():
            sensors.sendReadings()

    goToSleep()
