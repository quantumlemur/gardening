from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag
from esp32 import Partition
from ubinascii import hexlify
from machine import DEEPSLEEP_RESET, reset, reset_cause, Pin, Signal, unique_id


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


items = [
    ["Name", config.get("name")],
    ["ID", str(config.get("device_id"))],
    ["Board type", config.get("board_name")],
    ["MAC", hexlify(unique_id(), ":").decode()],
    ["Firmware", currentVersionTag],
    ["Partition", str(Partition(Partition.RUNNING).info()[4])],
    ["Server", config.get("server_url")],
]
# find widths
colWidths = [0, 0]
for item in items:
    for i in range(len(colWidths)):
        colWidths[i] = max(colWidths[i], len(item[i]))

print("start")
print(
    "{color}{fill:{fill}<{width}}".format(
        color=colors.HEADER, fill="-", width=(2 + colWidths[0] + 3 + colWidths[1] + 2)
    )
)
for item in items:
    print(
        "| {label: <{width0}}   {value: <{width1}} |".format(
            label=item[0],
            value=item[1],
            width0=colWidths[0],
            width1=colWidths[1],
        )
    )
print("{}{}".format("-" * (2 + colWidths[0] + 3 + colWidths[1] + 2), colors.ENDC))


print(colors.HEADER + "header")
print(colors.OKBLUE + "okblue")
print(colors.OKCYAN + "okcyan")
print(colors.OKGREEN + "okgreen")
print(colors.WARNING + "wanring")
print(colors.FAIL + "fail")
print(colors.BOLD + "bold")
print(colors.UNDERLINE + "underline")
