from machine import RTC
from time import sleep

# from blink import BlinkMessage
from sensors import Sensor
import utilities


moistureSensor = Sensor()
moistureSensor.storeReading()

try:
    moistureSensor.sendReadings()
except:
    pass

# blinker = BlinkMessage()
# blinker.genericBlink()

utilities.goToSleep()
