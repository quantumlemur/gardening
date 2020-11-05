from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal
from os import listdir, remove
from time import time


from boot import config
from currentVersionInfo import currentVersionHash, currentVersionTag


## Add in error checking around all config values


def now():
    return time() + 946684800


canaryFile = "__canary.py"


class Boot:
    def __init__(self):
        self.config = config.Config()

    def main(self):
        self.printBootInfo()

        if self.shouldConnectWifi():
            from boot import otaUpdater, updater, wifi

            wifiConnection = wifi.WifiConnection(self.config)
            wifiConnection.connect_wifi()

            self.config.put("LAST_INIT_TIME", now())
            self.config.put("NEXT_INIT_TIME", now() + self.config.get("INIT_INTERVAL"))
            self.config.updateFromServer()

            ota = otaUpdater.OTAUpdater(self.config)
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
                        reset()

            updater = updater.Updater(self.config)
            if updater.update_all_files():
                if canaryFile in listdir():
                    # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
                    part = Partition(Partition.RUNNING)
                    part.mark_app_valid_cancel_rollback()

    def printBootInfo(self):
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

    def setLED(self):
        ledPin = self.config.get("BOARD_LED_PIN")
        if ledPin and ledPin > 0:
            invert = self.config.get("BOARD_LED_PIN_INVERT") == 1
            on = self.config.get("LIGHT") == 1

            board_led = Signal(ledPin, Pin.OUT, invert=invert)
            if on:
                print("turning on LED")
                board_led.on()
            else:
                print("turning off LED")
                board_led.off()

    def shouldConnectWifi(self):
        return (
            reset_cause() != DEEPSLEEP_RESET
            or self.config.get("bootNum") == 0
            or now() >= self.config.get("NEXT_INIT_TIME")
            or self.config.get("firmware_update_in_progress")
        )


if __name__ == "__main__":
    boot = Boot()
    boot.main()

# set defaults
#


### Boot directory
# wifi connection
# config
# OTA updater
# default credentials
# file updater

# main takes the contents of MasterActions.