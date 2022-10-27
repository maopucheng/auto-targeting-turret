# 在这里写上你的代码 :-)
from machine import Pin # 导入Pin模块
from utime import sleep_ms #导入延时函数

led = Pin(22,Pin.OUT) # 构建led对象，GPIO22 输出

while True:
    led.value(0) # 点亮LED
    sleep_ms(1000)
    led.value(1) #熄灭LED灯
    sleep_ms(1000)
