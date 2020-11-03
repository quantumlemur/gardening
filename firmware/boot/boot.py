from esp32 import Partition
from machine import DEEPSLEEP_RESET, reset_cause
from time import time


from boot import *
from currentVersionInfo import currentCommitHash, currentCommitTag


def shouldConnectWifi():
    pass


if __name__ == "__main__":

    printBootInfo()

    config = config.Config()

    config.test()

    wifiConnection = wifi.WifiConnection(config)
    wifiConnection.connect_wifi()

    ota = otaUpdater.OTAUpdater(config)
    ota.checkAndUpdate()

# set defaults
#


### Boot directory
# wifi connection
# config
# OTA updater
# default credentials
# file updater

# main takes the contents of MasterActions.