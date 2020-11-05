from ubinascii import hexlify
import urequests
from utime import time

from machine import unique_id
from network import WLAN, STA_IF

import core.config
from currentVersionInfo import currentVersionHash, currentVersionTag


def now():
    """Returns unix timestamp, correcting for esp32 epoch"""
    return time() + 946684800


def isWifi():
    """Is wifi connected?"""
    return WLAN(STA_IF).isconnected()


def nextInitExpected():
    """Calculates the next time we expect that the device will boot and connect to wifi."""
    nextInitByTime = core.config.config.get("NEXT_INIT_TIME")
    nextInitByCount = now() + (
        core.config.config.get("MAX_ENTRYS_WITHOUT_INIT")
        - core.config.config.get("bootNum")
    ) * core.config.config.get("SLEEP_DURATION")
    nextInitExpected = min(nextInitByTime, nextInitByCount)
    return nextInitExpected


def _requestWrapper(method="GET", url=None, path=None, headers={}, **kwargs):
    """urequests wrapper.  Adds default headers to each request, and sets default
    server if not specified."""
    # Set path defaults
    if not url:
        url = core.config.config.get("server_url")
    if path:
        url = "{}/{}".format(url, path)
    # Build up default headers using live values
    fullHeaders = {
        "mac": hexlify(unique_id(), ":").decode(),
        "device-next-init": str(nextInitExpected()),
        "current-version-tag": currentVersionTag,
        "current-version-hash": currentVersionHash,
        "device-time": str(now()),
        "Content-Type": "application/json",
    }
    fullHeaders.update(headers)

    if method == "GET":
        return urequests.get(url=url, headers=fullHeaders, **kwargs)
    elif method == "POST":
        return urequests.get(url=url, headers=fullHeaders, **kwargs)
    else:
        print("Error: invalid request type")
        return None


def get(**kwargs):
    return _requestWrapper(method="GET", **kwargs)


def post(**kwargs):
    return _requestWrapper(method="POST", **kwargs)
