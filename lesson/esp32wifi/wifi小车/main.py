from car_ import Car
import time

car = Car(33, 35, 16, 18)
car.stop()


def car_action(act):
    act = act.split('_')
    if len(act) != 2:
        return
    try:
        act, speed = act[0], int(act[1])
    except:
        return
    if act == 'forw':
        car.forward(speed)
    if act == 'back':
        car.backward(speed)
    if act == 'left':
        car.left(speed)
    if act == 'right':
        car.right(speed)
    if act == 'stop':
        car.stop()


from serv.__main__ import start_server_
from serv.lib.esp32_ import ESP32_

esp32_ = ESP32_()
start_server_(80, 1, esp32_.html_, car_action)
