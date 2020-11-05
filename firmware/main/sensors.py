from time import sleep
from os import listdir, remove
from ujson import loads

from machine import ADC, Pin

from core.config import config
from core.utilities import now


def readAll():
    sensorList = config.get("SENSORS")
    print("sensorList:", sensorList)

    for s in sensorList:
        print("Defining sensor on pin {}".format(s["pin"]))
        Sensor(config, s["pin"], s["sensorName"], s["multiplier"]).takeReading()


def printFile():
    fname = config.get("sensorFile")
    with open(fname, "r") as f:
        print(f.read())


def sendReadings():
    fname = config.get("sensorFile")
    # remove(fname)

    success = False
    if fname in listdir():
        try:
            with open(fname, "r") as f:
                data = "{}]".format(f.read())
                print(data)
                url = "{}/readings".format(config.get("server_url"))
                headers = {
                    "device-next-init": str(config.get("next_init_expected")),
                    "Content-Type": "application/json",
                }

                request = post(url=url, headers=headers, data=data)
                if request.status_code == 200:
                    success = True
            if success:
                print("Sensor upload successful")
                remove(fname)
            else:
                print("Sensor upload unsuccessful.")
                # print(f.read())
        except Exception as err:
            print("========= Error during sensor send!  Trying deleting sensorfile")
            print(err)
            # print(traceback.format_exc())

            config.put("runningWithoutError", False)
            remove(fname)
    else:
        print("sensor file not found")


class Sensor:
    # dhtPin = machine.Pin(22, mode=machine.Pin.IN)
    # moisturePin = machine.Pin(32, mode=machine.Pin.IN)

    def __init__(self, config, pin, sensorName, multiplier=1):
        self.config = config
        self.pin = Pin(int(pin))
        self.sensorName = sensorName
        self.multiplier = float(multiplier)

        self.adc = ADC(self.pin)
        self.adc.atten(ADC.ATTN_11DB)

    def read(self):
        reading = self.adc.read()
        print(
            "Sensor {} reading: {}".format(self.sensorName, reading * self.multiplier)
        )
        return reading

    def takeReading(self):
        sensorString = '[{}, {}, 0, "{}"]'.format(
            now(), int(self.read() * self.multiplier), self.sensorName
        )

        fname = self.config.get("sensorFile")
        if fname not in listdir():
            with open(fname, "w") as f:
                f.write("[\n")
                f.write(sensorString)
        else:
            with open(fname, "a") as f:
                f.write(",\n{}".format(sensorString))

    # adc = machine.ADC(machine.Pin(32))
    # # set 11dB input attenuation (voltage range roughly 0.0v - 3.6v)
    # adc.atten(machine.ADC.ATTN_11DB)

    # print(adc.read())
    # for i in range(1, 32):
    #     print(i)
    #     try:
    #         pin = machine.Pin(i, mode=machine.Pin.IN)
    #         adc = machine.ADC(pin)
    #         print(i, adc.read_u16())
    #     except:
    #         pass
