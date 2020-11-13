from ubinascii import hexlify
import urequests
from utime import time

from machine import unique_id
from network import WLAN, STA_IF

import core.config
from currentVersionInfo import currentVersionHash, currentVersionTag


class colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

@micropython.native
def now():
    """Returns unix timestamp, correcting for esp32 epoch"""
    return time() + 946684800

@micropython.native
def isWifi():
    """Is wifi connected?"""
    return WLAN(STA_IF).isconnected()

@micropython.native
def nextInitExpected():
    """Calculates the next time we expect that the device will boot and connect to wifi."""
    nextInitByTime = core.config.config.get("NEXT_INIT_TIME")
    nextInitByCount = now() + (
        core.config.config.get("MAX_ENTRYS_WITHOUT_INIT")
        - core.config.config.get("bootNum")
    ) * core.config.config.get("SLEEP_DURATION")
    return min(nextInitByTime, nextInitByCount)

@micropython.native
def printTable(rows, header="", columnHeaders=[], color=""):
    """Formats, justifies, and prints a table of items."""
    # find widths
    contentWidths = [0] * len(rows[0])
    if columnHeaders:
        contentWidths = [len(header) for header in columnHeaders]
    for row in rows:
        contentWidths = [max(w, len(str(text))) for w, text in zip(contentWidths, row)]

    # Print header
    print(
        "{color} {bold}{underline} {header: <{width}}{endc}".format(
            color=color,
            bold=colors.BOLD,
            underline=colors.UNDERLINE,
            header=header,
            width=sum(contentWidths) + 2 * len(contentWidths),
            endc=colors.ENDC,
        )
    )

    # Print column headers
    if columnHeaders:
        for text, width in zip(columnHeaders, contentWidths):
            print(
                "{color}| {underline}{text: <{width}}{endc} ".format(
                    color=color,
                    underline=colors.UNDERLINE,
                    text=text,
                    width=width,
                    endc=colors.ENDC,
                ),
                end="",
            )
        print("{color}|{endc}".format(color=color, endc=colors.ENDC))

    # Print rows
    for row in rows:
        for text, width in zip(row, contentWidths):
            print(
                "{color}| {text: <{width}} ".format(
                    color=color,
                    text=str(text),
                    width=width,
                ),
                end="",
            )
        print("|{}".format(colors.ENDC))

    # Print bottom border
    print(
        "{color}{fill:{fill}<{width}}---{endc}".format(
            color=color,
            fill="-",
            width=(sum(contentWidths) + (2 * len(contentWidths))),
            endc=colors.ENDC,
        )
    )

@micropython.native
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

@micropython.native
def get(**kwargs):
    return _requestWrapper(method="GET", **kwargs)

@micropython.native
def post(**kwargs):
    return _requestWrapper(method="POST", **kwargs)
