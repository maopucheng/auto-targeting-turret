#引入硬件库
from machine import Pin,PWM
#引入随机库
import random as r

import time as t

#定义led控制对象
led1=Pin(16,Pin.OUT)
led2=Pin(17,Pin.OUT)
led3=Pin(18,Pin.OUT)
#开关
onof=Pin(19,Pin.OUT)
#嗡鸣器
wen=PWM(Pin(27),freq=1000)
wen.duty(0)
#定义舵机控制对象
pwm1=PWM(Pin(25),freq=50)
pwm2=PWM(Pin(26),freq=50)
pwm1.duty(90)
pwm2.duty(90)
#控制灯的高低电频0为低电频，1为高电频
led1.value(0)
led2.value(0)
led3.value(0)

onof.value(1)#初始化开关为高电频
st=0
list1=[]
#硬件连接测试函数
def restpwm():
    pwm1.duty(int(pwm1.duty())-30)
    t.sleep(0.5)
    pwm1.duty(int(pwm1.duty())+30)
    t.sleep(0.5)
    pwm1.duty(int(pwm1.duty())+30)
    t.sleep(0.5)
    pwm1.duty(int(pwm1.duty())-30)
    t.sleep(0.5)
    
    pwm2.duty(int(pwm2.duty())-30)
    t.sleep(0.5)
    pwm2.duty(int(pwm2.duty())+30)
    t.sleep(0.5)
    pwm2.duty(int(pwm2.duty())+30)
    t.sleep(0.5)
    pwm2.duty(int(pwm2.duty())-30)

#硬件连接测试函数
def restled():    
    for i in range(3):
        led1.value(1)
        led2.value(1)
        led3.value(1)
        t.sleep(0.5)
        led1.value(0)
        led2.value(0)
        led3.value(0)
        t.sleep(0.5)

def wmq(s,n,p):
    for i in range(n):
        wen.duty(p)
        t.sleep(s)
        wen.duty(0)
        t.sleep(s)

#随机led
def randomled():
    
    led1.value(1)
    wmq(0.2,1,500)
    t.sleep(r.randint(1,10)*0.1)
    led1.value(0)
    wmq(0.2,1,0)
    t.sleep(r.randint(1,10)*0.1)
    led2.value(1)
    wmq(0.2,1,500)
    t.sleep(r.randint(1,10)*0.1)
    led2.value(0)
    wmq(0.2,1,0)
    t.sleep(r.randint(1,10)*0.1)
    led3.value(1)
    wmq(0.2,1,500)
    t.sleep(r.randint(1,10)*0.1)
    led3.value(0)
    wmq(0.2,1,0)
    t.sleep(r.randint(1,10)*0.1)

list1=[]
def randompwm():   
    while True:
        ran=r.randint(1,4)
        if ran not in list1:
            list1.append(ran)
            break
    
    if ran==1:
        pwm1.duty(int(pwm1.duty())-30)
        t.sleep(0.5)
        pwm1.duty(int(pwm1.duty())+30)
    elif ran==2:
        pwm1.duty(int(pwm1.duty())+30)
        t.sleep(0.5)
        pwm1.duty(int(pwm1.duty())-30)
    elif ran==3:
        pwm2.duty(int(pwm2.duty())-30)
        t.sleep(0.5)
        pwm2.duty(int(pwm2.duty())+30)
    else:
        pwm2.duty(int(pwm2.duty())+30)
        t.sleep(0.5)
        pwm2.duty(int(pwm2.duty())-30)
        

def star():
    print('开始')
    for i in range(4):
        randomled()
        wmq(1,1,500)
        randompwm()
        t.sleep(1)
    


    


while True:
    if int(onof.value())==0:
        t.sleep(0.1)
        if int(onof.value())!=0:
            if st==0:
                st=1
                star()
                #复位变量
                st=0
                list1=[]
                
                
            


    



