# boot.py can handle checking for a new boot.py (really, main.py), ensuring that it runs ok, and if not then falling back to the old one!
# To implement that, all this stuff should be moved to main.py


# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

# import main

from machine import WDT
from machine import Timer
from os import listdir, remove, rename
from time import sleep, time

import machine


# config
maxboots = 2
sleeptime = 5 * 1000  # milliseconds

# Set watchdog timer
wdt = WDT(timeout=60000)  # milliseconds

# start processing
# unhold the pin.  Is this necessary?
# p16 = machine.Pin(16, machine.Pin.OUT, None)
# led = machine.Signal(16, machine.Pin.OUT, invert=True)
# led.on()


def now():
    return time() + 946684800


doConnectWifi = False


# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
else:
    doConnectWifi = True


# check for new files downloaded last boot
for filename in listdir():
    if filename[-4:] == ".new":
        print("renaming file from {} to {}".format(filename, filename[:-4]))
        rename(filename, filename[:-4])
        doConnectWifi = True


try:
    from config import Config
    config = Config()

    p16 = machine.Pin(config.get('ledPin'), machine.Pin.OUT, None)
    led = machine.Signal(config.get('ledPin'),
                         machine.Pin.OUT, invert=True)
    if config.get('LIGHT') == 1:
        print('turning on LED')
        led.on()
    else:
        print('turning off LED')
        led.off()

    if config.get('bootNum') == 0 or now() >= config.get('NEXT_INIT_TIME') or not config.get('runningWithoutError'):
        doConnectWifi = True
except:
    doConnectWifi = True


if doConnectWifi:
    from wifi import WifiConnection
    from updater import Updater

    wifiConnection = WifiConnection()

    wifiConnection.connect_wifi()

    wifiConnection.monitor_connection()

    # Try
    try:
        from config import Config
        config = Config()
        config.put('runningWithoutError', False)
        config.updateFromServer()
        config.put('LAST_INIT_TIME', now())
        config.put('NEXT_INIT_TIME', now() +
                   config.get('INIT_INTERVAL'))
        sleep(1)  # Why is this here?
    except:
        pass

    updater = Updater()
    if updater.update_all_files():
        # Reboot if any files were downloaded
        machine.reset()
