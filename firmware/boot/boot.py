from boot import config, otaUpdater, wifi


def printBootInfo():
    print("==============================")
    print("Time: {}".format(time()))
    part = Partition(Partition.RUNNING)
    print(part.info())
    from currentCommitHash import currentCommitHash, currentCommitTag

    print(
        "Current version: {}.  Commit hash: {}".format(
            currentCommitTag, currentCommitHash
        )
    )
    print("==============================")


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