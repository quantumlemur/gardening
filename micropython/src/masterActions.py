from machine import RTC, Pin, ADC
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

# sensorReadPin = Pin(33, Pin.IN, None)
# adc = ADC(sensorReadPin)
# adc.atten(ADC.ATTN_11DB)

# for i in range(50):
#     print(adc.read())
#     sleep(.1)


utilities.goToSleep()
