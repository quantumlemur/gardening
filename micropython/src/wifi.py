from machine import reset
from network import STA_IF, WLAN
from ntptime import settime
from time import sleep, time
from ubinascii import hexlify


class WifiConnection:
    def __init__(self, config, led=None):
        self.config = config
        self.led = led
        self.wifi = WLAN(STA_IF)
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
                self.config.get("wifi_ssid"), self.config.get("wifi_password")
            )
            wifiConnectStartTime = time()
            while not self.wifi.isconnected():
                sleep(0.1)
                if time() > wifiConnectStartTime + 20:
                    print("Wifi connect timed out.  restarting...")
                    reset()

            try:
                if self.led:
                    self.led.set_rgb_cycle(
                        [
                            (1, 0, 1, 0),
                            (1, 0, 1, 1),
                            (1, 0, 0, 1),
                            (1, 0, 1, 1),
                            (1, 0, 0, 0),
                        ]
                    )
                settime()
            except OSError:
                print("NTP sync failed")

    def monitor_connection(self):
        if self.wifi.isconnected():
            # cloud.set_asset_state("counter", counter)
            # print("Counter sent: {}".format(counter))
            print("Network config:", self.wifi.ifconfig())
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
