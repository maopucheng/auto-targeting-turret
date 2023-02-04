import socket
import utime
import network
import _thread
from machine import Pin
from lib.microdot_asyncio import Microdot, Response
from lib.microdot_utemplate import render_template

SSID = "dou_mi"
PASSWORD = "bcm123456"
led = Pin(2, Pin.OUT)


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
Response.default_content_type = 'text/html'


@app.route('/')
async def hello(request):
    return render_template('index.html', status="let's start!")


def flash_led():
    for i in range(50):
        led.value(0)
        utime.sleep(0.05)
        led.value(1)
        utime.sleep(0.05)


@app.route('/light')
async def light(request):
    print(request.args)
    try:
        if request.args['switch'] == 'on':
            led.value(1)
            print('on')
            return render_template('index.html', status="ON")
        elif request.args['switch'] == 'off':
            led.value(0)
            print('off')
            return render_template('index.html', status="OFF")
        elif request.args['switch'] == 'flash':
            print('flash')
            _thread.start_new_thread(flash_led, ())
            return render_template('index.html', status="Flash")
        else:
            print('nothing')

    except Exception as err:
        print(err)
        return '[ERROR] ' + str(err)


def start_server():
    print('Starting Web server at http://{}:{}'.format(ip, 80))
    try:
        app.run(port=80)
    except:
        app.shutdown()
        print('Shutdown!')


start_server()
