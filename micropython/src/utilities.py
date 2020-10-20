import machine

from config import Config


config = Config()


def goToSleep(quickSleep=False):

    if config.get('bootNum') < config.get('MAX_ENTRYS_WITHOUT_INIT'):
        config.put('bootNum', config.get('bootNum') + 1)
    else:
        config.put('bootNum', 0)

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

    config.put('runningWithoutError', True)

    if quickSleep:
        machine.deepsleep(1000)
    else:
        machine.deepsleep(config.get("SLEEP_DURATION") * 1000)
