from machine import UART
import machine
import ubinascii
import esp32
import select

from time import sleep

print(ubinascii.hexlify(machine.unique_id(), ':').decode())
print(dir(machine))
print(dir(esp32))
print(esp32.raw_temperature())

uart1 = UART(1, 115200)
uart2 = UART(2, 115200)
# uart3 = UART(3, 115200)


for i in range(10):
    print("=============================")
    print("=================== UART1 {}".format(uart1.any()))
    print("=================== UART2 {}".format(uart2.any()))
    # print("=================== UART3 {}".format(uart3.any()))
    print("=============================")
    sleep(1)


poll = select.poll()
poll.register(uart1, select.POLLIN)
print(poll.poll(10))
