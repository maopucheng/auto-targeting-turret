import socket
import utime
import network
from machine import Pin


SSID = "MT"
PASSWORD = "87654321"
led = Pin(22, Pin.OUT)


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

conn, addr = webserver.accept()  # 接受一个连接，conn是一个新的socket对象

while True:

    # print("in %s" % str(addr))
    request = conn.recv(1024)  # 从套接字接收1024字节的数据
    print(request)
    if len(request) > 0:
        request = request.decode().strip()
        print(request)
        if request == "on":
            led.value(0)
            conn.send("yes,sir! on!")
            print("light on")
        elif request == "off":
            led.value(1)
            conn.send("yes,sir! off!")
            print("light off")
        elif request == "shutdown":
            break
        else:
            conn.send("nothing happened!")
            print("light not change")
    else:
        print("no request string")


conn.close()
print("connection closed!")
