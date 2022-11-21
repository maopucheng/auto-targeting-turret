import socket
import utime
import network
from machine import Pin

SSID = "dou_home"
PASSWORD = "chinaaaa"
led = Pin(22, Pin.OUT)


def do_connect(ssid, password):
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)

    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        print("connect failed!")
        if utime.time() - start > 20:
            print("connect timeout!")
            break

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())
