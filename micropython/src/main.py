from machine import RTC
from network import WLAN, STA_IF
from time import sleep

# from blink import BlinkMessage
from sensors import Sensor
import utilities


wifiIsConnected = WLAN(STA_IF).isconnected()

moistureSensor = Sensor()
moistureSensor.storeReading()

if wifiIsConnected:
    moistureSensor.sendReadings()

# blinker = BlinkMessage()
# blinker.genericBlink()

utilities.goToSleep()
