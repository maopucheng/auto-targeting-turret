import socket
import utime
import network
from machine import Pin
from servo import Servo

led = Pin(2,Pin.OUT)
bottom = 25 #25, 33, 32
upper = 33
Servo = Servo()
# Servo.angle(90, bottom)
# utime.sleep(2)
Servo.angle(120, upper)
utime.sleep(2)
