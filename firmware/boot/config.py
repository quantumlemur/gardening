from ubinascii import hexlify
import btree
from ujson import loads, dumps
from uos import listdir, remove
from urequests import get
from utime import time

from machine import unique_id, WDT


DBFILE = "btree.db"


def now():
    return time() + 946684800


from currentVersionInfo import currentVersionHash, currentVersionTag


class Config:
    wdt = WDT(timeout=120000)  # milliseconds

    def __init__(self):
        self.db = None
        try:
            f = open(DBFILE, "r+b")
            self.db = btree.open(f)

        except OSError:
            print("{} not found.  Reinitializing database.".format(DBFILE))
            f = open(DBFILE, "w+b")
            self.db = btree.open(f)
            self.reinitialize()

        print(self.get("server_url"))

    def reinitialize(self):
        defaults = {
            b"LAST_ENTRY_TIME": b"0",
            b"LAST_INIT_TIME": b"0",
            b"NEXT_INIT_TIME": b"0",
            b"MAX_ENTRYS_WITHOUT_INIT": b"2",
            b"ENTRYS_SINCE_INIT": b"0",
            b"INIT_INTERVAL": b"10",
            b"SLEEP_DURATION": b"1",
            b"LIGHT": b"1",
            b"DHT_PIN": b"0",
            b"bootNum": b"0",
            b"next_init_expected": b"0",
            b"mac": str(hexlify(unique_id(), ":")),
            b"ledPin": b"16",
            b"runningWithoutError": b"false",
            b"firmware_update_in_progress": b"false",
            b"sensorFile": b'"sensorfile"',
            b"server_url": b'"http://nuc/device"',
            b"wifi_ssid": b'"julia&mike-guest"',
            b"wifi_password": b'"welcometothebarnyard"',
            b"requested_version_tag": b"null",
        }
        for key, value in defaults.items():
            self.db[key] = value
            print(key, self.db[key])
        self.db.flush()

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
        self.db.flush()

    def get(self, key):
        if key in self.db:
            return loads(self.db[key])
        else:
            return None

    def put(self, key, value):
        self.db[key.encode()] = dumps(value).encode()

    def updateFromServer(self):
        self.calcNextInitExpected()
        url = "{}/config".format(self.config["server_url"])
        print("Checking for server config updates from {}".format(url))
        headers = {
            "mac": str(self.config["mac"]),
            "device-next-init": str(self.config["next_init_expected"]),
            "current-version-tag": str(currentVersionTag),
            "current-version-hash": str(currentVersionHash),
            "device-time": str(now()),
            "Content-Type": "application/json",
        }
        print(headers)
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
