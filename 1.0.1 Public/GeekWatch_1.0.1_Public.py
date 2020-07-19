import time
from mpython import *
from machine import Timer
import network
import ntptime
import json
import urequests
import framebuf
import font.digiface_21

def Time():
    global monthnumber, time_s2, time_s1, walk, kcal, Watch, Month
    time_s1 = ''.join([str(x) for x in [time.localtime()[3] // 10, time.localtime()[3] % 10, ":", time.localtime()[4] // 10, time.localtime()[4] % 10]])
    time_s2 = str(time.localtime()[5] // 10) + str(time.localtime()[5] % 10)
    monthnumber = time.localtime()[6]

_is_shaked = _is_thrown = False
_last_x = _last_y = _last_z = _count_shaked = _count_thrown = 0
def on_shaked():pass
def on_thrown():pass

tim11 = Timer(11)

def timer11_tick(_):
    global _is_shaked, _is_thrown, _last_x, _last_y, _last_z, _count_shaked, _count_thrown
    if _is_shaked:
        _count_shaked += 1
        if _count_shaked == 5: _count_shaked = 0
    if _is_thrown:
        _count_thrown += 1
        if _count_thrown == 10: _count_thrown = 0
        if _count_thrown > 0: return
    x=accelerometer.get_x(); y=accelerometer.get_y(); z=accelerometer.get_z()
    _is_thrown = (x * x + y * y + z * z < 0.25)
    if _is_thrown: on_thrown();return
    if _last_x == 0 and _last_y == 0 and _last_z == 0:
        _last_x = x; _last_y = y; _last_z = z; return
    diff_x = x - _last_x; diff_y = y - _last_y; diff_z = z - _last_z
    _last_x = x; _last_y = y; _last_z = z
    if _count_shaked > 0: return
    _is_shaked = (diff_x * diff_x + diff_y * diff_y + diff_z * diff_z > 1)
    if _is_shaked: on_shaked()

tim11.init(period=100, mode=Timer.PERIODIC, callback=timer11_tick)

def Sport():
    global monthnumber, time_s2, time_s1, walk, kcal, Watch, Month
    if _is_shaked:
        walk = walk + 1
        kcal = walk // 50

def Watch_Logic():
    global monthnumber, time_s2, time_s1, walk, kcal, Watch, Month
    Month = ["一", "二", "三", "四", "五", "六", "日"]
    Watch = [str("周") + str(Month[monthnumber]), ''.join([str(x) for x in [time.localtime()[1], "/", time.localtime()[2]]]), str(time_s1), ''.join([str(x) for x in ["卡路里:", kcal, "kcal"]]), ''.join([str(x) for x in ["步数:", walk, "步"]]), w1["results"][0]["now"]["text"], ""]
    if touchPad_P.read() < 400:
        Watch = ["我的状态", "", str(walk), ''.join([str(x) for x in ["已消耗", kcal, "Kcal"]]), str(time_s1), "", "步"]
    if touchPad_Y.read() < 400:
        Watch = ["实时天气", w1["results"][0]["location"]["name"], w1["results"][0]["now"]["temperature"], w1["results"][0]["last_update"][:10], ''.join([str(x) for x in ["最高", w2["results"][0]["daily"][0]["high"], " 最低", w2["results"][0]["daily"][0]["low"]]]), "", "摄氏度"]
    if touchPad_T.read() < 400:
        Watch = ["明日天气预报", w1["results"][0]["location"]["name"], ''.join([str(x) for x in ["H", w2["results"][0]["daily"][1]["high"], " L", w2["results"][0]["daily"][1]["low"]]]), "", w2["results"][0]["daily"][1]["text_day"], "", ""]
    if touchPad_O.read() < 400:
        Watch = ["二维码", " ", " ", "", "", "", ""]
        myUI.qr_code("输入你要显示的文本", 55, 0, scale=1)
    if touchPad_N.read() < 400:
        Watch = ["系统版本", "", str("v1.0.1"), "Geek Watch OS", str(" 开发 ") + str("Dennis Huang"), "", ""]

my_wifi = wifi()

my_wifi.connectWiFi("在这里输入您的WiFi名称", "在这里输入您的WiFi密码")

myUI = UI(oled)

def get_seni_weather(_url, _location):
    _url = _url + "&location=" + _location.replace(" ", "%20")
    response = urequests.get(_url)
    json = response.json()
    response.close()
    return json

def display_font(_font, _str, _x, _y, _wrap, _z=0):
    _start = _x
    for _c in _str:
        _d = _font.get_ch(_c)
        if _wrap and _x > 128 - _d[2]: _x = _start; _y += _d[1]
        if _c == '1' and _z > 0: oled.fill_rect(_x, _y, _d[2], _d[1], 0)
        oled.blit(framebuf.FrameBuffer(bytearray(_d[0]), _d[2], _d[1],
        framebuf.MONO_HLSB), (_x+int(_d[2]/_z)) if _c=='1' and _z>0 else _x, _y)
        _x += _d[2]


ntptime.settime(8, "ntp.ntsc.ac.cn")
oled.fill(0)
walk = 0
kcal = 0
w1 = get_seni_weather("https://api.seniverse.com/v3/weather/now.json?key=SvW_zfVWUgR0dbqBp", "ip")
w2 = get_seni_weather("https://api.seniverse.com/v3/weather/daily.json?key=SvW_zfVWUgR0dbqBp", "ip")
while True:
    oled.fill(0)
    Sport()
    Time()
    Watch_Logic()
    oled.DispChar((str(Watch[0])), 0, 0, 1)
    oled.DispChar((str(Watch[1])), 102, 0, 1)
    display_font(font.digiface_21, Watch[2], 35, 15, False, 2)
    oled.DispChar((str(Watch[3])), 0, 35, 1)
    oled.DispChar((str(Watch[4])), 0, 49, 1)
    oled.DispChar((str(Watch[5])), 100, 49, 1)
    oled.DispChar((str(Watch[6])), 65, 20, 1)
    oled.show()
