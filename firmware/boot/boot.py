from boot import config, otaUpdater, wifi

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