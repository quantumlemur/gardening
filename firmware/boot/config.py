from json import loads, dumps
from time import time
from ubinascii import hexlify
from urequests import get

from os import listdir, remove
from machine import unique_id, WDT

CONFIGFILE = "config.json"


def now():
    return time() + 946684800


from currentVersionInfo import currentVersionHash, currentVersionTag


class Config:
    wdt = WDT(timeout=120000)  # milliseconds

    config = {
        "LAST_ENTRY_TIME": 0,
        "LAST_INIT_TIME": 0,
        "NEXT_INIT_TIME": 0,
        "MAX_ENTRYS_WITHOUT_INIT": 2,
        "ENTRYS_SINCE_INIT": 0,
        "INIT_INTERVAL": 10,
        "SLEEP_DURATION": 1,
        "LIGHT": 1,
        "DHT_PIN": 0,
        "bootNum": 0,
        "next_init_expected": 0,
        "mac": str(hexlify(unique_id(), ":").decode()),
        "ledPin": 16,
        "runningWithoutError": False,
        "firmware_update_in_progress": False,
        "sensorFile": "sensorfile",
        "server_url": "http://nuc/device",
        "wifi_ssid": "julia&mike-guest",
        "wifi_password": "welcometothebarnyard",
        "requested_version_tag": "",
    }

    def __init__(self):
        self.load()

    def test(self):
        print("config test: {}".format(currentVersionTag))

    def load(self):
        """Loads config from disk"""
        if CONFIGFILE in listdir():
            try:
                originalConfigLength = len(self.config)
                with open(CONFIGFILE, "r") as f:
                    configFromFile = loads(f.read())
                    self.config.update(configFromFile)
            except ValueError:
                print("========= config file corrupt; removing")
                remove(CONFIGFILE)
        else:
            print("No config file found.  Saving defaults")
        # Reload the onboard config details
        self.config["mac"] = str(hexlify(unique_id(), ":").decode())
        self.save()

    def save(self):
        with open(CONFIGFILE, "w") as f:
            f.write(dumps(self.config))

    def get(self, item):
        if item in self.config:
            return self.config[item]
        else:
            return None

    def put(self, item, value):
        self.load()
        self.config[item] = value
        self.save()

    def updateFromServer(self):
        self.calcNextInitExpected()
        url = "{}/config".format(self.config["server_url"])
        print("Checking for server config updates from {}".format(url))
        headers = {
            "mac": str(self.config["mac"]),
            "device_next_init": str(self.config["next_init_expected"]),
            "current_version_tag": str(currentVersionTag),
            "current_version_hash": str(currentVersionHash),
            "device_time": str(now()),
            "Content-Type": "application/json",
        }
        request = get(url=url, headers=headers)
        if request.status_code == 200:
            print("Server config update successful")
            configFromServer = request.json()
            print(configFromServer)
            if configFromServer:
                # Validate new server URL before storing it...
                previousServerUrl = self.config["server_url"]
                if self.config["server_url"] != configFromServer["server_url"]:
                    print("New server URL found.  Validating...")
                    newUrl = "{}/config".format(configFromServer["server_url"])
                    try:
                        request = get(url=newUrl, headers=headers)
                        if request.status_code == 200:
                            print("New server URL validated successfully.  Saving!")
                        else:
                            print("New server URL failed validation.  Reverting.")
                            configFromServer["server_url"] = previousServerUrl
                    except OSError:
                        print("New server URL failed validation.  Reverting.")
                        configFromServer["server_url"] = previousServerUrl
                self.config.update(configFromServer)
                self.save()
                self.calcNextInitExpected()
            else:
                print("Error: server returned no config")
        else:
            print("Error: server update fetch unsuccessful")
        # request.close()

    def calcNextInitExpected(self):
        nextInitByTime = self.config["NEXT_INIT_TIME"]
        nextInitByCount = (
            now()
            + (self.config["MAX_ENTRYS_WITHOUT_INIT"] - self.config["bootNum"])
            * self.config["SLEEP_DURATION"]
        )
        nextInitExpected = min(nextInitByTime, nextInitByCount)
        self.put("next_init_expected", nextInitExpected)


if __name__ == "__main__":
    from wifi import WifiConnection

    wifiConnection = WifiConnection()
    wifiConnection.connect_wifi()

    config = Config()
    config.updateFromServer()
