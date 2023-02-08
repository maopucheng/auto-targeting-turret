import socket
import utime
import network
from machine import Pin
from servo import Servo

led = Pin(2, Pin.OUT)
# 可用引脚由下往上为 22, 32, 25
bottom = 22
upper = 32
Servo = Servo()
Servo.angle(90, bottom)
utime.sleep(1)
Servo.angle(100, upper)
utime.sleep(1)

SSID = "dou_mi"
PASSWORD = "bcm123456"

# f = open('error.log', mode='at')
# f.write("-------start--------\n")


def do_connect():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)

    start = utime.time()
    while not wlan.isconnected():
        utime.sleep(1)
        print("connect failed!")
        if utime.time() - start > 20:
            print("connect timeout!")
            break

    if wlan.isconnected():
        print('network config:', wlan.ifconfig())


sta_if = network.WLAN(network.STA_IF)
do_connect()
ip = sta_if.ifconfig()[0]

port = 1080

webserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建套接字
webserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 设置给定套接字选项的值
# webserver.settimeout(2000)
webserver.bind((ip, port))  # 绑定IP地址和端口号
webserver.listen(5)  # 监听套接字
print("Socks服务器地址:%s:%d" % (ip, port))
# f.write("Socks服务器地址:%s:%d" % (ip, port)+"\n")

conn, addr = webserver.accept()  # 接受一个连接，conn是一个新的socket对象
angles = [90, 100]


while True:
    try:
        request = conn.recv(1024)  # 从套接字接收1024字节的数据
        if len(request) > 0:
            request = request.decode().strip()
            print('request: ', request)
            # f.write('request: '+request+"\n")
            request = request.split('#')[0:-1]  # 切片去除最后一个空白字符串
            for pos in request:
                bottom_ang, upper_ang = [int(x) for x in pos.split(',')]
                print('bottom & upper angle: ', bottom_ang, upper_ang)
                # f.write('bottom & upper angle: '+str(pos)+"\n")
                Servo.angle(bottom_ang, bottom)
                Servo.angle(upper_ang, upper)
    except Exception as e:
        print("error: " + str(e))
        # f.write("error: "+str(e)+"\n")
        # f.close()
        # f = open('error.log',mode='at')

# f.write("---------------end----------\n")
# f.close()
conn.close()
print("connection closed!")
