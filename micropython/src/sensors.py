import machine
import urequests

from time import sleep, time
from os import listdir, remove

from credentials import credentials
from config import Config

config = Config()


class Sensor:
    # dhtPin = machine.Pin(22, mode=machine.Pin.IN)
    # moisturePin = machine.Pin(32, mode=machine.Pin.IN)

    def __init__(self):
        self.pin = machine.Pin(32)
        self.adc = machine.ADC(self.pin)
        self.adc.atten(machine.ADC.ATTN_11DB)

    def read(self):
        return self.adc.read()

    def storeReading(self):
        sensorString = '[{}, {}, 0, "soil"]'.format(
            time()+946684800, self.read())

        fname = config.get("sensorFile")
        if fname not in listdir():
            with open(fname, 'w') as f:
                f.write("[\n")
                f.write(sensorString)
        else:
            with open(fname, 'a') as f:
                f.write(",\n{}".format(sensorString))

    def printFile(self):
        fname = config.get("sensorFile")
        with open(fname, 'r') as f:
            print(f.read())

    def sendReadings(self):
        fname = config.get("sensorFile")
        # remove(fname)

        success = False
        if fname in listdir():
            with open(fname, 'r') as f:
                data = f.read() + ']'
                print(data)
                url = "{}/readings".format(credentials['server_url'])
                headers = {
                    "mac": str(config.get("mac")),
                    "device-next-init": str(config.get("next_init_expected")),
                    "Content-Type": "application/json",
                }

                request = urequests.post(url=url, headers=headers, data=data)
                if request.status_code == 200:
                    success = True
            if success:
                print("Sensor upload successful")
                remove(fname)
            else:
                print("Sensor upload unsuccessful")
                # print(f.read())
        else:
            print('sensor file not found')


if __name__ == "__main__":
    sensor = Sensor()
    sensor.sendReadings()

    # print(sensor.read())

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
