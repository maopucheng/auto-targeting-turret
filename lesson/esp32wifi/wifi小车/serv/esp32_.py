# ESP 32
# 这个文件包含两个线程，一个是WIFI链接的，另一个是板上LED的

import machine
import time, network, json
from .http_ import Http_


def time_str_():
    t_ = time.localtime(time.time())
    return '%d/%d/%d %d:%d.%d' % (t_[0], t_[1], t_[2], t_[3], t_[4], t_[5])


class ESP32_:
    def __init__(self):
        self.config = None
        self.load_config()

        self.onboard_led = machine.Pin(self.config['led_pin'], machine.Pin.OUT)

        self.ap_if = network.WLAN(network.AP_IF)
        if self.config is not None:
            if 'essid' in self.config:
                self.ap_if.config(essid=self.config['essid'])
            if 'password' in self.config:
                self.ap_if.config(password=self.config['password'])
        self.ap_if.active(True)
        print(
            'ESP32 本地热点配置:', self.ap_if.ifconfig()
        )  #  IP address, netmask, gateway, DNS

        self.sta_if = network.WLAN(network.STA_IF)
        self.ip_addr = None

        self.is_connected_ = False
        with open('wifi_index.html') as fp:
            self.html_tempt = fp.read()

        if self.config is not None:
            self.connect()

    def load_config(self):
        try:
            with open('esp32_config.json') as fp:
                self.config = json.load(fp)
        except:
            self.config = None

    def save_config(self):
        with open('esp32_config.json', 'w') as fp:
            json.dump(self.config, fp)

    def connect(self, wait_time=60):
        self.onboard_led.on()
        self.sta_if.active(False)
        self.sta_if.active(True)
        self.is_connected_ = False
        try:
            self.sta_if.connect(self.config['ap_name'], self.config['ap_pwd'])
            self.ip_addr = 'ESP32 正在连接 %s ...' % self.config['ap_name']
            print(self.ip_addr)
        except OSError as ex:
            self.ip_addr = 'ESP32 异常 ' + str(ex)
            print(self.ip_addr)
            self.sta_if.active(False)
            self.onboard_led.on()
            return
        start_time_ = time.time()
        while not self.sta_if.isconnected():
            if time.time() - start_time_ > wait_time:
                break
        if self.sta_if.isconnected():
            self.is_connected_ = True
            self.onboard_led.off()
            self.ip_addr = '[%s] %s (%s)' % (
                self.config['ap_name'],
                self.sta_if.ifconfig()[0],
                time_str_(),
            )
            print('ESP32 已连接: ', self.ip_addr)
        else:
            self.ip_addr = 'ESP32 未能连接到 %s' % self.config['ap_name']
            print(self.ip_addr)
            self.sta_if.active(False)
            self.onboard_led.on()

    def get_html_(self):
        if self.config is None:
            ap_name = ap_pwd = ''
        else:
            ap_name, ap_pwd = self.config['ap_name'], self.config['ap_pwd']
        return self.html_tempt % (
            ap_name,
            '',
            '未连接无线网络' if self.ip_addr is None else self.ip_addr,
        )

    def html_(self, request_, response_, route_args_):
        print('ESP32 连接', request_.addr_)
        params_ = request_.params_
        if 'ap_name' in params_ and 'ap_pwd' in params_:
            if (
                self.config['ap_name'] != params_['ap_name']
                or self.config['ap_pwd'] != params_['ap_pwd']
            ):
                self.config['ap_name'] = params_['ap_name']
                self.config['ap_pwd'] = params_['ap_pwd']
                self.save_config()
                self.connect()
            else:
                print('ESP32 与已有网络配置相同:', self.config['ap_name'])
        response_.write_response_OK_(
            content_type_="text/html", content_=self.get_html_(), charset_='UTF-8'
        )
