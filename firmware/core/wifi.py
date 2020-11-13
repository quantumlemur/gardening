from ntptime import settime
from utime import sleep, time, ticks_ms, ticks_diff
from ubinascii import hexlify

from machine import reset
from network import STA_IF, WLAN

from core.config import config
from core.utilities import colors

from uos import urandom

wifi = WLAN(STA_IF)


@micropython.native
def connect_wifi():
    startTime = ticks_ms()
    ifconfig = config.get("ifconfig")
    if ifconfig:
        print("Previous wifi config found.  Loading: {}".format(ifconfig))
        wifi.ifconfig(ifconfig)

    config.put("ifconfig", None)  # Erase stored config so it's reset on error
    config.flush()

    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to wifi...")
        wifi.connect(config.get("wifi_ssid"), config.get("wifi_password"))
        wifiConnectStartTicks = ticks_ms()
        while (ticks_diff(ticks_ms(), wifiConnectStartTicks) < 20000) and (
            not wifi.isconnected()
        ):
            sleep(0.1)
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
        config.put(
            "ifconfig", wifi.ifconfig()
        )  # Store successful wifi config for next time
        print("wifi time: {}".format(ticks_diff(ticks_ms(), startTime)))
        return True
    except OSError:
        print("NTP sync failed")
        wifi.active(False)
        return False
    print("Shouldn't be able to end up here.  Wifi problem?")
    wifi.active(False)
    return False


@micropython.native
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
