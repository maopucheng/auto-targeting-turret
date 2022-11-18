from L298N_ import DCMotor
from machine import Pin


class Car:
    def __init__(self, left1, left2, right1, right2):
        self.motor_left = DCMotor(left1, left2)
        self.motor_right = DCMotor(right1, right2)
        self.stop()

    def stop(self):
        self.motor_left.stop()
        self.motor_right.stop()

    def forward(self, speed):
        self.motor_left.forward(speed)
        self.motor_right.forward(speed)

    def backward(self, speed):
        self.motor_left.backward(speed)
        self.motor_right.backward(speed)

    def left(self, speed):
        self.motor_left.backward(speed)
        self.motor_right.forward(speed)

    def right(self, speed):
        self.motor_left.forward(speed)
        self.motor_right.backward(speed)
