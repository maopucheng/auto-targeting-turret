from machine import Pin
import time as t

p12 = Pin(12, Pin.OUT)   # create output pin on GPIO0
p13 = Pin(13, Pin.OUT)
p17 = Pin(17, Pin.OUT)

j=0
n=1
for i in range(10):
    p12.value(n)                
    p13.value(j) 
    p17.value(j) 
    t.sleep(0.2)
    if j==0:
        j=1
    else:
        j=0
    if n==0:
        n=1
    else:
        n=0




    
