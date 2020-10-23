# import esp
# esp.osdebug(None)


from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal, Timer, WDT
from os import listdir, remove, rename
from time import sleep, time


# file imports
from config import Config

config = Config()

# Set watchdog timer
wdt = WDT(timeout=60000)  # milliseconds


def now():
    return time() + 946684800


p16 = Pin(config.get("ledPin"), Pin.OUT, None)
led = Signal(config.get("ledPin"), Pin.OUT, invert=True)
if config.get("LIGHT") == 1:
    print("turning on LED")
    led.on()
else:
    print("turning off LED")
    led.off()


###################### Wifi connection checks ######################


upgradeSuccessFile = "__UPGRADE_SUCCESSFUL"
upgradeFile = "__UPGRADE_IN_PROGRESS"
doConnectWifi = False


# check if the device woke from a deep sleep
if reset_cause() == DEEPSLEEP_RESET:
    print("woke from a deep sleep")
else:
    doConnectWifi = True

# make sure we connect to wifi and run the updater if we're in the middle of an upgrade
if upgradeFile in listdir():
    doConnectWifi = True

# check for new files downloaded last boot
for filename in listdir():
    if filename[-4:] == ".new":
        print("renaming file from {} to {}".format(filename, filename[:-4]))
        rename(filename, filename[:-4])
        doConnectWifi = True

if (
    config.get("bootNum") == 0
    or now() >= config.get("NEXT_INIT_TIME")
    or not config.get("runningWithoutError")
):
    doConnectWifi = True


###################### Wifi connection ######################


if doConnectWifi:
    from wifi import WifiConnection
    from updater import Updater

    wifiConnection = WifiConnection(config)

    wifiConnection.connect_wifi()

    wifiConnection.monitor_connection()

    config.put("runningWithoutError", False)
    config.put("LAST_INIT_TIME", now())
    config.put("NEXT_INIT_TIME", now() + config.get("INIT_INTERVAL"))
    config.updateFromServer()
    sleep(1)  # Why is this here?

    updater = Updater(config)
    if updater.update_all_files():
        print("Updater found new files")
        if upgradeFile in listdir():
            print("Upgrade in progress, updater succeeded.  Writing success file.")
            # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
            with open(upgradeSuccessFile, "w") as f:
                f.write("zzz")

        # Reboot if any files were downloaded
        reset()


###################### Main actions ######################


try:
    from masterActions import MasterActions

    masterActions = MasterActions(config)
    masterActions.run()
except Exception as err:
    print("MasterActions failed import.  Rebooting.")
    print(err)
    reset()
