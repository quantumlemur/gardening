import network
import urequests
from ntptime import settime
from ubinascii import hexlify


from credentials import credentials


class WifiConnection:

    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)
        # Try to store the mac if the config module is working
        # print("mac address: " + hexlify(self.wifi.config('mac'), ':'))

        # try:
        #     from config import Config
        #     config = Config()
        #     print("mac address: " + hexlify(self.wifi.config('mac'), ':'))
        #     config.put('mac', ubinascii.hexlify(machine.unique_id(), ':').decode()))
        # except:
        #     pass

        # self.url = "https://api.allthingstalk.io/device/{}/state".format(
        #     device_id)
        # self.headers = {"Authorization": "Bearer {}".format(device_token),
        #                 "Content-type": "application/json", }

    def connect_wifi(self):
        self.wifi.active(True)
        if not self.wifi.isconnected():
            print("Connecting to wifi...")
            self.wifi.connect(
                credentials["wifi_ssid"], credentials["wifi_password"])
            while not self.wifi.isconnected():
                pass
            settime()

    def monitor_connection(self):
        if self.wifi.isconnected():
            # cloud.set_asset_state("counter", counter)
            # print("Counter sent: {}".format(counter))
            print('Network config:', self.wifi.ifconfig())
            # counter += 1
        else:
            self.connect_wifi()

    # def set_asset_state(self, asset_name, asset_state):
    #     data = {asset_name: {"value": asset_state}}
    #     self.put_data(data)

    # def set_multiple(self, asset_states):
    #     data = {}
    #     for key in asset_states:
    #         data[key] = {"value": asset_states[key]}
    #     self.put_data(data)

    # def put_data(self, data):
    #     request = urequests.put(self.url, headers=self.headers, json=data)
    #     request.close()
