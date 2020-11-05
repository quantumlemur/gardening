from ubinascii import hexlify
import urequests
from utime import time

from machine import unique_id
from network import WLAN, STA_IF

from currentVersionInfo import currentVersionHash, currentVersionTag


def now():
    return time() + 946684800


def isWifi():
    return WLAN(STA_IF).isconnected()


def post(url, headers={}, **kwargs):
    fullHeaders = {
        "mac": str(hexlify(unique_id(), ":").decode()),
        "current-version-tag": str(currentVersionTag),
        "current-version-hash": str(currentVersionHash),
        "device-time": str(now()),
    }
    fullHeaders.update(headers)
    return urequests.post(url=url, headers=fullHeaders, **kwargs)
