from machine import WDT

wdt = WDT(timeout=120000)  # milliseconds


from ubinascii import hexlify
from uos import listdir, remove
from utime import localtime, time

from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal, unique_id

from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag
from core.utilities import colors, nextInitExpected, now, printTable

######
## Anything non-essential to OTA updates should be enclosed in try...except blocks
######

canaryFile = "__canary.py"
bootError = False


@micropython.native
def main():
    global bootError
    try:
        config.put("bootsSinceWifi", config.get("bootsSinceWifi") + 1)
    except Exception as e:
        bootError = True
        print("Error setting bootnum")
    printBootInfo()
    setLED()

    if shouldConnectWifi():
        from core import otaUpdater, updater, wifi

        if not wifi.connect_wifi():
            print("Wifi connection failed.  Moving on without wifi...")
            return
            # config.close()
            # reset()
        try:
            config.put("bootsSinceWifi", 0)
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
                    if canaryFile in listdir():
                        remove(canaryFile)
                    ota.setNextBoot()
                    print("Firmware download successful.  Rebooting...")
                    config.close()
                    reset()

        if updater.update_all_files():
            if canaryFile in listdir():
                # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
                part = Partition(Partition.RUNNING)
                part.mark_app_valid_cancel_rollback()


@micropython.native
def printBootInfo():
    global bootError
    try:
        items = [
            ["Name", config.get("name")],
            ["ID", str(config.get("device_id"))],
            ["Board type", config.get("board_name")],
            ["MAC", hexlify(unique_id(), ":").decode()],
            ["Firmware", currentVersionTag],
            ["Partition", str(Partition(Partition.RUNNING).info()[4])],
            ["Server", config.get("server_url")],
            [
                "Boots since last connection",
                "{} of {}".format(
                    config.get("bootsSinceWifi"), config.get("MAX_ENTRYS_WITHOUT_INIT")
                ),
            ],
            [
                "Current time",
                "{}-{}-{} {}:{}:{}".format(*localtime(time() - 60 * 60 * 8)),
            ],
        ]
        printTable(
            items,
            header="Boot Info",
            color=colors.HEADER,
        )

    except Exception as e:
        bootError = True
        print("Error in boot.printBootInfo(): ", e)


@micropython.native
def setLED():
    global bootError
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
        bootError = True
        print("Error in boot.setLED():", e)


@micropython.native
def shouldConnectWifi():
    global bootError
    try:
        wifiReasons = [
            ["Clock at 0", time() == 0],
            ["Non-sleep boot", reset_cause() != DEEPSLEEP_RESET],
            [
                "Boot count",
                config.get("bootsSinceWifi") >= config.get("MAX_ENTRYS_WITHOUT_INIT"),
            ],
            ["Boot time", now() >= config.get("NEXT_INIT_TIME")],
            [
                "Firmware_update_in_progress",
                config.get("firmware_update_in_progress"),
            ],
            ["Config: Not runningWithoutError", not config.get("runningWithoutError")],
            ["canaryFile missing", canaryFile not in listdir()],
            ["bootError", bootError],
            ["Wifi config empty", config.get("ifconfig") is None],
        ]
        shouldConnect = False
        for reason, value in wifiReasons:
            if value:
                shouldConnect = True
        if shouldConnect:
            printTable(
                [[reason] for reason, value in wifiReasons if value],
                header="Connecting to wifi because...",
            )
        return shouldConnect
    except Exception as e:
        bootError = True
        print("Error in boot.shouldConnectWifi():", e)
        return True


if __name__ == "__main__":
    main()

# set defaults
#

self._db
self._db
self._db
### Boot directory
# wifi connection
# config
# OTA updater
# default credentials
# file updater

# main takes the contents of MasterActions.