from machine import Timer
import dht
import machine

d=dht.DHT11(machine.Pin(4))
def f(t):
    d.measure()
    a=d.temperature()
    b=d.humidity()
    print('�¶�:',a,'��C')
    print('ʪ��:',b,'%')

tim = Timer(-1)  #�½�һ�����ⶨʱ��
tim.init(period=2000, mode=Timer.PERIODIC, callback=f)