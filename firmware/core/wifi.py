from ntptime import settime
from utime import sleep, time
from ubinascii import hexlify

from machine import reset
from network import STA_IF, WLAN

from core.config import config


wifi = WLAN(STA_IF)
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


def connect_wifi():
    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to wifi...")
        wifi.connect(config.get("wifi_ssid"), config.get("wifi_password"))
        wifiConnectStartTime = time()
        while not wifi.isconnected():
            sleep(0.1)
            if time() > wifiConnectStartTime + 20:
                print("Wifi connect timed out.")
                return False

        try:
            # if led:
            #     led.set_rgb_cycle(
            #         [
            #             (1, 0, 1, 0),
            #             (1, 0, 1, 1),
            #             (1, 0, 0, 1),
            #             (1, 0, 1, 1),
            #             (1, 0, 0, 0),
            #         ]
            #     )
            settime()
        except OSError:
            print("NTP sync failed")
    return True


def monitor_connection():
    if wifi.isconnected():
        # cloud.set_asset_state("counter", counter)
        # print("Counter sent: {}".format(counter))
        print("Network config:", wifi.ifconfig())
        # counter += 1
    else:
        connect_wifi()

    # def set_asset_state( asset_name, asset_state):
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
