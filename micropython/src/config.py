from json import loads, dumps
from time import time
from ubinascii import hexlify
from urequests import get

from os import listdir, remove
from machine import unique_id

CONFIGFILE = "config.json"


def now():
    return time() + 946684800


class Config:
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
        "sensorFile": "sensorfile",
        "server_url": "http://nuc/device",
        "wifi_ssid": "julia&mike-guest",
        "wifi_password": "welcometothebarnyard",
    }

    def __init__(self):
        self.load()

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
        self.config["server_url"] = "http://nuc/device"
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
            "device-next-init": str(self.config["next_init_expected"]),
            "Content-Type": "application/json",
        }
        request = get(url=url, headers=headers)
        if request.status_code == 200:
            print("Server config update successful")
            configFromServer = request.json()
            print(configFromServer)
            if configFromServer:
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
