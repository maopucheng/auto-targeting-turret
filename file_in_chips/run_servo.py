# Required Code
# 1. import servo_angles                       #Imports Module
# 2. Servo = servo_angles.servo                #Call the class variable anything you want but adapt the bellow building blocks
#'Do the Action' Code                       #Bellow assumes you called the class variable (Required 2.) to Servo. If you did not: Adapt the bollow where says Servo.the_feature.
# 1. Servo.angle(angle, pin number)         #Sets the servo angle to the first positional argument(angle), for the pin number in the seccond positional argument (pin number) ** See Bottom
# 2. A_Variable = (Servo.convert_pwm(90))   #(Servo.convert_pwm(angle)) returns the required Pwm value to reach the required variable.
# 3. Servo.pwm(pwm_value, pin number)       #Sets the servo in the given pin number to the given pwm value.

from servo import Servo
from machine import Pin
import utime

led = Pin(2,Pin.OUT)
bottom = 33 #25, 33, 32
upper = 32
Servo = Servo()
Servo.angle(30, bottom)
utime.sleep(1)
Servo.angle(30, upper)
utime.sleep(1)
print("outter of for")

i = 0
while True:
    i+=1
    led.value(i%2)
    print("from 30, stop 3 sec")
    utime.sleep(2)
    for i in range(30,150):
        Servo.angle(i, bottom)
        Servo.angle(i, upper)  
        utime.sleep(0.02) 
    print("get 150")
    utime.sleep(1)
    for i in range(150,30,-1):  
        Servo.angle(i, bottom)  
        Servo.angle(i, upper)  
        utime.sleep(0.02)  
    print("get 30")