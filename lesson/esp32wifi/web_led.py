import socket
import utime
import network
from machine import Pin
import uasyncio
from microdot_asyncio import Microdot
from microdot_utemplate import render_template

SSID = "dou_home"
PASSWORD = "chinaaaa"
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

# setup webserver
app = Microdot()


@app.route('/')
async def hello(request):
    return render_template('index.html',hhh=)


@app.route('/light')
async def light(request):
    print(request.args)
    try:
        if request.args['switch'] == 'on':
            led.value(0)
            print('on')
            return 'led on'
        elif request.args['switch'] == 'off':
            led.value(1)
            print('off')
            return 'led off'
        else:
            print('nothing')
            return 'nothing happened'
    except Exception as err:
        print(err)
        return '[ERROR] ' + str(err)


def start_server():
    print('Starting Web server at http://{}:{}'.format(ip, 80))
    try:
        app.run(port=80)
    except:
        app.shutdown()
        print('Starting failed!')


start_server()
