import time
from machine import Pin


l1 = Pin(2, Pin.OUT)
l2 = Pin(25, Pin.OUT)

while True:
    l1.value(1)
    l2.value(1)
    time.sleep(0.5)
    l1.value(0)
    l2.value(0)
    time.sleep(0.5)

