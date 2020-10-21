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

from config import Config

config = Config()

# Set watchdog timer
wdt = WDT(timeout=60000)  # milliseconds

# start processing
# unhold the pin.  Is this necessary?
# p16 = machine.Pin(16, machine.Pin.OUT, None)
# led = machine.Signal(16, machine.Pin.OUT, invert=True)
# led.on()


def now():
    return time() + 946684800


p16 = machine.Pin(config.get('ledPin'), machine.Pin.OUT, None)
led = machine.Signal(config.get('ledPin'),
                     machine.Pin.OUT, invert=True)
if config.get('LIGHT') == 1:
    print('turning on LED')
    led.on()
else:
    print('turning off LED')
    led.off()


upgradeSuccessFile = '__UPGRADE_SUCCESSFUL'
upgradeFile = '__UPGRADE_IN_PROGRESS'
doConnectWifi = False


# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')
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

if config.get('bootNum') == 0 or now() >= config.get('NEXT_INIT_TIME') or not config.get('runningWithoutError'):
    doConnectWifi = True


# sensorVPin = machine.Pin(25, machine.Pin.OUT, None)
# sensorVPin.on()
# sensorGPin = machine.Pin(26, machine.Pin.OUT, None)
# sensorGPin.off()

# sensorReadPin = machine.Pin(33, machine.Pin.IN, None)
# adc = machine.ADC(sensorReadPin)
# adc.atten(machine.ADC.ATTN_11DB)


if doConnectWifi:
    from wifi import WifiConnection
    from updater import Updater

    wifiConnection = WifiConnection()

    wifiConnection.connect_wifi()

    wifiConnection.monitor_connection()

    config.put('runningWithoutError', False)
    config.put('LAST_INIT_TIME', now())
    config.put('NEXT_INIT_TIME', now() +
               config.get('INIT_INTERVAL'))
    config.updateFromServer()
    sleep(1)  # Why is this here?

    updater = Updater()
    if updater.update_all_files():
        print('Updater found new files')
        if upgradeFile in listdir():
            print('Upgrade in progress, updater succeeded.  Writing success file.')
            # if we're in an update, we should've at least downloaded the canary, so we're guaranteed to be here if all is well
            with open(upgradeSuccessFile, 'w') as f:
                f.write('zzz')

        # Reboot if any files were downloaded
        machine.reset()


try:
    import masterActions
except:
    print('MasterActions failed import.  Rebooting.')
    machine.reset()
