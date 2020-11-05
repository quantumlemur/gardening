from ubinascii import hexlify
from ujson import loads, dumps

from machine import unique_id, WDT


mac = hexlify(unique_id(), ":")
print(mac)
j = dumps(mac).encode()
print(type(j), j)
o = loads(j)
print(type(o), o)