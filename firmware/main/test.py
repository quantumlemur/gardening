from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag
from esp32 import Partition
from ubinascii import hexlify
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal, unique_id
from utime import time, localtime


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


print(colors.HEADER + "header")
print(colors.OKBLUE + "okblue")
print(colors.OKCYAN + "okcyan")
print(colors.OKGREEN + "okgreen")
print(colors.WARNING + "wanring")
print(colors.FAIL + "fail")
print(colors.BOLD + "bold")
print(colors.UNDERLINE + "underline" + colors.ENDC)


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
                    text=text,
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


items = [
    ["Name", config.get("name")],
    ["ID", str(config.get("device_id"))],
    ["Board type", config.get("board_name")],
    ["MAC", hexlify(unique_id(), ":").decode()],
    ["Firmware", currentVersionTag],
    ["Partition", str(Partition(Partition.RUNNING).info()[4])],
    ["Server", config.get("server_url")],
    [
        "Boots since last connection",
        "{} of {}".format(
            config.get("bootsSinceWifi"), config.get("MAX_ENTRYS_WITHOUT_INIT")
        ),
    ],
    [
        "Current time",
        "{}-{}-{} {}:{}:{}".format(*localtime(time() - 60 * 60 * 8)),
    ],
]
printTable(
    items,
    header="Boot Info",
    # columnHeaders=["text", "value"],
    # color=colors.HEADER,
)