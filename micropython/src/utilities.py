import machine
from time import time, sleep

from config import Config


config = Config()


def now():
    return time() + 946684800


def goToSleep(quickSleep=False):

    sleep_duration = max(min(config.get('SLEEP_DURATION'),
                             config.get('NEXT_INIT_TIME') - now()), 1)
    print('Boot number {} of {}'.format(config.get(
        'bootNum'), config.get('MAX_ENTRYS_WITHOUT_INIT')))
    print('Boot time {} of {}.  {} seconds until connection'.format(
        now(), config.get('NEXT_INIT_TIME'), config.get('NEXT_INIT_TIME') - now()))

    # bootNum == 0 signifies to connect to wifi next boot
    if time() == 0:
        print("*** Connecting to wifi next boot, and not sleeping.  Reason: clock at 0")
        sleep_duration = 1
    elif now() + config.get('SLEEP_DURATION') >= config.get('NEXT_INIT_TIME'):
        print("*** Connecting to wifi next boot.  Reason: next sleep would pass the next connection time.")
        config.put('bootNum', 0)
    elif config.get('bootNum') >= config.get('MAX_ENTRYS_WITHOUT_INIT'):
        print("*** Connecting to wifi next boot.  Reason: max num of non-connection boots reached.")
        config.put('bootNum', 0)
    else:
        print("*** Sleeping and booting like normal, not connecting to wifi next boot.")
        config.put('bootNum', config.get('bootNum') + 1)

    # with open("BOOTNUM", "rb") as f:
    #     # bootnum = f.read()
    #     print('new boot num: {}'.format(bootnum))
    led = machine.Signal(config.get('ledPin'), machine.Pin.OUT, invert=True)
    led.off()

    # Get ready to go to sleep
    # hold the pin to prevent current leakage.  is this necessary?
    # p4 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_HOLD)
    # hold the pin to prevent current leakage.  is this necessary?
    p16 = machine.Pin(config.get('ledPin'), machine.Pin.IN,
                      machine.Pin.PULL_HOLD)
    # p25 = machine.Pin(25, machine.Pin.IN, machine.Pin.PULL_HOLD)
    # p26 = machine.Pin(26, machine.Pin.IN, machine.Pin.PULL_HOLD)

    config.put('runningWithoutError', True)

    if quickSleep:
        machine.deepsleep(1000)
    else:
        machine.deepsleep(config.get("SLEEP_DURATION") * 1000)
