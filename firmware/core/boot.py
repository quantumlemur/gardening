from uos import listdir, remove
from utime import time

from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal

from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag
from core.utilities import now


## Add in error checking around all config values

canaryFile = "__canary.py"


def main():
    printBootInfo()

    if shouldConnectWifi():
        from core import otaUpdater, updater, wifi

        if not wifi.connect_wifi():
            print("Wifi connection failed.  Restarting...")
            config.close()
            reset()

        config.put("LAST_INIT_TIME", now())
        config.put(
            "NEXT_INIT_TIME",
            now() + config.get("INIT_INTERVAL"),
        )
        config.updateFromServer()
        config.flush()

        ota = otaUpdater.OTAUpdater()
        desiredVersion = ota.getDesiredVersion()
        if desiredVersion:
            print(
                "New firmware found!  {} => {}".format(
                    currentVersionTag, desiredVersion["filename"][:-4]
                )
            )
            if ota.updateFirmware(version=desiredVersion):
                if ota.verifyHash():
                    ota.setNextBoot()
                    if canaryFile in listdir():
                        remove(canaryFile)
                    print("Firmware download successful.  Rebooting...")
                    config.close()
                    reset()

        if updater.update_all_files():
            if canaryFile in listdir():
                # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
                part = Partition(Partition.RUNNING)
                part.mark_app_valid_cancel_rollback()


def printBootInfo():
    print("==============================")
    print("Booting at time: {}".format(time()))
    part = Partition(Partition.RUNNING)
    print(part.info())

    print(
        "Current version: {}  Commit hash: {}".format(
            currentVersionTag, currentVersionHash
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
    return (
        reset_cause() != DEEPSLEEP_RESET
        or config.get("bootNum") == 0
        or now() >= config.get("NEXT_INIT_TIME")
        or config.get("firmware_update_in_progress")
        or not config.get("running_without_error")
    )


if __name__ == "__main__":
    main()
    config.close()

# set defaults
#


### Boot directory
# wifi connection
# config
# OTA updater
# default credentials
# file updater

# main takes the contents of MasterActions.