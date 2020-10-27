from machine import UART
import machine
import ubinascii
import esp32
import select
from urequests import get
import socket

from time import sleep

# print(ubinascii.hexlify(machine.unique_id(), ':').decode())
# print(dir(machine))
# print(dir(esp32))
# print(esp32.raw_temperature())

# uart1 = UART(1, 115200)
# uart2 = UART(2, 115200)
# # uart3 = UART(3, 115200)


# for i in range(10):
#     print("=============================")
#     print("=================== UART1 {}".format(uart1.any()))
#     print("=================== UART2 {}".format(uart2.any()))
#     # print("=================== UART3 {}".format(uart3.any()))
#     print("=============================")
#     sleep(1)


# poll = select.poll()
# poll.register(uart1, select.POLLIN)
# print(poll.poll(10))


# sensorVPin = machine.Pin(25, machine.Pin.OUT)
# sensorVPin.on()

# sensorReadPin = machine.Pin(33, machine.Pin.IN)
# adc = machine.ADC(sensorReadPin)
# adc.atten(machine.ADC.ATTN_11DB)
# print(adc.read())

# url = "http://192.168.86.20:5000/static/firmware.bin"
# with get(url=url, stream=True) as r:
#     r.raise_for_status()
#     with open("firmware.bin", "w") as f:
#         for chunk in r.iter_content(chunk_size=8192):
#             f.write(chunk)


# import requeststream

# url = "http://192.168.86.20:5000/static/firmware.bin"
# r = requeststream.get(url=url)
# print(r.status_code)


# addr = socket.getaddrinfo("192.168.86.20", 5000)[0][-1]
# method = "GET"
# path = "/static/firmware.bin"
# header_string = "Host: %s\r\n" % "http://192.168.86.20:5000"
# request = b"%s %s HTTP/1.0\r\n%s" % (method, path, header_string)
# # print(request)
# addr = (b"192.168.86.20", 5000)
# s = socket.socket()
# s.settimeout(10)
# s.connect(addr)
# request = b"GET /static/firmware.bin HTTP/1.0\r\nHost: 192.168.86.20\r\n\r\n"
# s.send(request)
# with open("firmware.bin", "w") as f:
#     while 1:
#         print("inside loop")
#         recv = s.recv(1024)
#         if len(recv) == 0:
#             break
#         f.write(recv)
# s.close()


from currentCommitHash import CurrentCommitHash

print(CurrentCommitHash.currentCommitHash)