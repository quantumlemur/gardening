from ubinascii import hexlify
from uos import listdir, remove
from utime import time

from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal, unique_id

from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag
from core.utilities import colors, now

######
## Anything non-essential to OTA updates should be enclosed in try...except blocks
######

canaryFile = "__canary.py"


def main():
    printBootInfo()
    setLED()

    if shouldConnectWifi():
        from core import otaUpdater, updater, wifi

        if not wifi.connect_wifi():
            print("Wifi connection failed.  Restarting...")
            config.close()
            reset()
        try:
            config.put("LAST_INIT_TIME", now())
            config.put(
                "NEXT_INIT_TIME",
                now() + config.get("INIT_INTERVAL"),
            )
            config.flush()
        except Exception as e:
            print("Error in boot.main(), updating init times: ", e)
        try:
            config.updateFromServer()
            config.flush()
        except Exception as e:
            print("Error in boot.main(), pulling config updates from server: ", e)

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
    try:
        items = [
            ["Name", config.get("name")],
            ["ID", str(config.get("device_id"))],
            ["Board type", config.get("board_name")],
            ["MAC", hexlify(unique_id(), ":").decode()],
            ["Firmware", currentVersionTag],
            ["Partition", str(Partition(Partition.RUNNING).info()[4])],
            ["Server", config.get("server_url")],
        ]
        # find widths
        colWidths = [0, 0]
        for item in items:
            for i in range(len(colWidths)):
                colWidths[i] = max(colWidths[i], len(item[i]))

        print(
            "{color}{fill:{fill}<{width}}".format(
                color=colors.HEADER,
                fill="-",
                width=(2 + colWidths[0] + 3 + colWidths[1] + 2),
            )
        )
        for item in items:
            print(
                "| {label: <{width0}}   {value: <{width1}} |".format(
                    label=item[0],
                    value=item[1],
                    width0=colWidths[0],
                    width1=colWidths[1],
                )
            )
        print(
            "{fill:{fill}<{width}}{color}".format(
                color=colors.ENDC,
                fill="-",
                width=(2 + colWidths[0] + 3 + colWidths[1] + 2),
            )
        )
    except Exception as e:
        print("Error in boot.printBootInfo(): ", e)


def setLED():
    try:
        ledPin = config.get("BOARD_LED_PIN")
        if ledPin and ledPin > 0:
            invert = config.get("BOARD_LED_PIN_INVERT") == 1
            on = config.get("LIGHT") == 1

            # Pin(self.config.get("G_LED_PIN"), mode=Pin.OUT, pull=None)
            board_led = Signal(ledPin, Pin.OUT, pull=None, invert=invert)
            if on:
                print("turning on LED, pin {}, invert {}".format(ledPin, invert))
                board_led.on()
            else:
                print("turning off LED, pin {}, invert {}".format(ledPin, invert))
                board_led.off()
    except Exception as e:
        print("Error in boot.setLED():", e)


def shouldConnectWifi():
    try:
        wifiReasons = {
            "reset_cause != DEEPSLEEP_RESET": reset_cause() != DEEPSLEEP_RESET,
            'config.get("bootNum") == 0': config.get("bootNum") == 0,
            'now() >= config.get("NEXT_INIT_TIME")': now()
            >= config.get("NEXT_INIT_TIME"),
            'config.get("firmware_update_in_progress")': config.get(
                "firmware_update_in_progress"
            ),
            'not config.get("runningWithoutError")': not config.get(
                "runningWithoutError"
            ),
        }
        shouldConnect = False
        for reason, value in wifiReasons.items():
            if value:
                shouldConnect = True
                print("Wifi reason: {}".format(reason))
        return shouldConnect
    except Exception as e:
        print("Error in boot.shouldConnectWifi():", e)
        return True


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