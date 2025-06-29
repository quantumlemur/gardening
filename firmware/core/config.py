from ubinascii import hexlify
import btree
from ujson import loads, dumps
from uos import listdir, remove

# from urequests import get
from utime import time, ticks_ms

from machine import unique_id
import core.utilities

DBFILE = "btree.db"


from currentVersionInfo import currentVersionHash, currentVersionTag


class Config:
    def __init__(self):
        """Opens the database, recreating it if necessary."""
        self._f = None
        self._db = None
        try:
            self._f = open(DBFILE, "r+b")
            self._db = btree.open(self._f)
            if b"wifi_ssid" not in self._db:
                self.reinitialize()
        except Exception as err:
            print("Database load error: {}.  Reinitializing database.".format(err))
            self._f = open(DBFILE, "w+b")
            self._db = btree.open(self._f)
            self.reinitialize()

    @micropython.native
    def reinitialize(self):
        """Recreates the default values in the database"""
        defaults = {
            "LAST_ENTRY_TIME": 0,
            "LAST_INIT_TIME": 0,
            "NEXT_INIT_TIME": 0,
            "MAX_ENTRYS_WITHOUT_INIT": 2,
            "ENTRYS_SINCE_INIT": 0,
            "INIT_INTERVAL": 10,
            "SLEEP_DURATION": 1,
            "LIGHT": 1,
            "DHT_PIN": 0,
            "bootsSinceWifi": 0,
            "ledPin": 16,
            "runningWithoutError": False,
            "firmware_update_in_progress": False,
            "requested_version_tag": None,
            "name": "",
            "device_id": None,
        }
        for key, value in defaults.items():
            self.put(key, value)

        # Reload credentials
        from core.credentials import credentials

        for key, value in credentials.items():

            self.put(key, value)
        self.flush()

    @micropython.native
    def flush(self):
        """Flushes the database to disk"""
        self._db.flush()
        self._f.flush()

    @micropython.native
    def get(self, key, raw=False):
        """Gets a value from the database, optionally skipping json decoding"""
        if key in self._db:
            # print("getting {}".format(key))
            # print("getting {} from {}".format(self._db[key.encode()], key))
            item = self._db[key.encode()]
            return item if raw else loads(item)
        else:
            return None

    @micropython.native
    def put(self, key, value):
        """Puts a value into the database.
        Returns: bool whether anything changed"""
        # print("putting {} {} in {} {}".format(type(value), str(value), type(key), key))
        # res = dumps(value).encode()
        # print(
        #     "Encoded: {} {}".format(
        #         type(value), str(value), type(key), key, type(res), res
        #     )
        # )
        if value != self.get(key):
            self._db[key.encode()] = dumps(value).encode()
            return True
        return False

    @micropython.native
    def updateFromServer(self):
        """Fetches a new config from the server and updates the database with it.  Returns whether anything changed."""
        print('start of update')
        print(
            "Checking for server config updates from {}".format(self.get("server_url"))
        )
        dbChanged = False
        request = core.utilities.get(path="config")
        if request.status_code == 200:
            print("Server config successfully pulled")
            configFromServer = request.json()
            if configFromServer:
                # First, check if we have a new server url, and validate it before storing (or we'd lock ourselves out if it's invalid)
                previousServerUrl = self.get("server_url")
                if self.get("server_url") != configFromServer["server_url"]:
                    print("New server URL found.  Validating...")
                    try:
                        request = core.utilities.get(
                            url=configFromServer["server_url"], path="config"
                        )
                        if request.status_code == 200:
                            print(
                                "New server URL validated successfully.  Storing it, and the new config!"
                            )
                            dbChanged = True
                            configFromServer = request.json()
                        else:
                            print("New server URL failed validation.  Reverting.")
                            configFromServer["server_url"] = previousServerUrl
                    except OSError:
                        print("New server URL failed validation.  Reverting.")
                        configFromServer["server_url"] = previousServerUrl
                for key, value in configFromServer.items():
                    try:  # try to unpack json strings if they exist from the server
                        value = loads(value)
                    except (TypeError, ValueError) as e:
                        pass

                    if value != self.get(key):  # only update if the value is changed
                        print("updating {} in config".format(key))
                        print("old: ", self.get(key))
                        print("new: ", value)

                        self.put(key, value)
                        dbChanged = True

        else:
            print("Error: server update fetch unsuccessful")
        return dbChanged

    @micropython.native
    def wipe(self):
        """Complete erase and reset of config"""
        self.close()
        remove(DBFILE)
        self.__init__()

    @micropython.native
    def close(self):
        self.flush()
        self._db.close()
        self._f.close()

    @micropython.native
    def __del__(self):
        self.close()


# The persistent instance of config
config = Config()

if __name__ == "__main__":
    from core import wifi

    wifiConnection = wifi.WifiConnection()
    wifiConnection.connect_wifi()

    config.updateFromServer()
