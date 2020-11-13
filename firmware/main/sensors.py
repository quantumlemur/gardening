from ujson import loads
from uos import listdir, remove
from utime import sleep

import btree
from machine import ADC, Pin

from core.config import config
from core.utilities import now, post


READINGSFILE = "readings.db"


class Sensors:
    def __init__(self):
        """Opens the database, recreating it if necessary."""
        self._f = None
        self._db = None
        try:
            self._f = open(READINGSFILE, "r+b")
            self._db = btree.open(self._f)
        except Exception as err:
            print("Database load error: {}.  Reinitializing database.".format(err))
            self._f = open(READINGSFILE, "w+b")
            self._db = btree.open(self._f)
            self._db[b"nextSlot"] = b"0"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._db.close()
        self._f.close()

    @micropython.native
    def readSensors(self):
        """Read all sensors and store in database"""
        db = self._db
        sensorList = config.get("SENSORS")
        for s in sensorList:
            adc = ADC(Pin(s["pin"]))
            adc.atten(ADC.ATTN_11DB)
            reading = int(adc.read() * s["multiplier"])
            readingString = b'{},{},0,"{}"'.format(now(), reading, s["sensorName"])
            print(readingString)

            # store in database and increment counter
            nextSlot = db[b"nextSlot"]
            db[nextSlot] = readingString
            db[b"nextSlot"] = str(int(nextSlot) + 1).encode()

    # def printFile(self):
    #     fname = config.get("sensorFile")
    #     with open(fname, "r") as f:
    #         print(f.read())

    @micropython.native
    def sendReadings(self):
        db = self._db
        try:
            numReadings = int(db[b"nextSlot"])
            data = ""
            for i in range(numReadings):
                if i == 0:
                    data = "[{}]".format(db[str(i)].decode())
                else:
                    data = "{},[{}]".format(data, db[str(i)].decode())
            data = "[{}]".format(data)
            request = post(path="readings", data=data)
            if request.status_code == 200:
                print("Sensor upload successful")
                for i in range(numReadings):
                    del db[str(i).encode()]
                db[b"nextSlot"] = b"0"
            else:
                print("Sensor upload unsuccessful.")
        except KeyError as e:
            print("Sensor database error.  Resetting data...")
            db[b"nextSlot"] = b"0"

    @micropython.native
    def wipe(self):
        """Removes and resets the database file"""
        self._db.close()
        self._f.close()
        remove(READINGSFILE)
        self.__init__()
