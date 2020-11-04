from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset_cause, Pin, Signal
from os import listdir
from time import time


from boot import config, otaUpdater, wifi
from currentVersionInfo import currentCommitHash, currentCommitTag


canaryFile = "__canary.py"
config = config.Config()


def main():
    printBootInfo()

    if shouldConnectWifi():

        wifiConnection = wifi.WifiConnection(config)
        wifiConnection.connect_wifi()

        config.put("LAST_INIT_TIME", now())
        config.put("NEXT_INIT_TIME", now() + config.get("INIT_INTERVAL"))
        config.updateFromServer()

        ota = otaUpdater.OTAUpdater(config)
        ota.checkAndUpdate()

        updater = updater.Updater(config)
        if updater.update_all_files():
            if canaryFile in listdir():
                # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
                part = Partition(Partition.RUNNING)
                part.mark_app_valid_cancel_rollback()


def now():
    return time() + 946684800


def printBootInfo():
    print("==============================")
    print("Booting at time: {}".format(time()))
    part = Partition(Partition.RUNNING).info()
    print(part.info())

    print(
        "Current version: {}.  Commit hash: {}".format(
            currentCommitTag, currentCommitHash
        )
    )
    print("==============================")


def setLED():
    ledPin = config.get("BOARD_LED_PIN")
    if ledPin and ledPin > 0:
        invert = config.get("BOARD_LED_PIN_INVERT") == 1
        on = config.get("LIGHT") == 1

        board_led = Signal(ledPin, Pin.OUT, invert=invert)
        if on:
            print("turning on LED")
            board_led.on()
        else:
            print("turning off LED")
            board_led.off()


def shouldConnectWifi():
    if (
        reset_cause() != DEEPSLEEP_RESET
        or config.get("bootNum") == 0
        or now() >= config.get("NEXT_INIT_TIME")
        or config.get("firmware_update_in_progress")
    ):
        return True
    else:
        return False


if __name__ == "__main__":
    main()

# set defaults
#


### Boot directory
# wifi connection
# config
# OTA updater
# default credentials
# file updater

# main takes the contents of MasterActions.