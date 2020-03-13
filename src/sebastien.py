# coding:utf-8
import json
import time
import RPi.GPIO as GPIO
from speak import Speak, NluMetaData
import speak
import os.path as osp
import sys
import smbus
ver = (sys.version_info.major, sys.version_info.minor)
inspath = '../.lib/lib/python%d.%d/site-packages' % ver
sys.path.insert(0, osp.abspath(inspath))

is_started = False

# init GPIO
GPIO.setmode(GPIO.BCM)
servo_gpio = 5
GPIO.setup(servo_gpio, GPIO.OUT)
servo = GPIO.PWM(servo_gpio, 50)

mute_after_play = True

# init I2C
i2c = smbus.SMBus(3)
sensor_addr = 0x68
sensor_conf = 0b10011000
i2c.write_byte(sensor_addr, sensor_conf)

check_sensor = False
sensor_buff = []
sensor_threshold = 0

# https://www.denshi.club/pc/raspi/5raspberry-pi-zeroiot4a-d1-3.html
def swap16(x):
        return (((x << 8) & 0xFF00) |
                ((x >> 8) & 0x00FF))
def sign16(x):
        return ( -(x & 0b1000000000000000) |
                  (x & 0b0111111111111111) )

sdk = None


def mute():
    print("mute")
    global sdk
    sdk.mute()


def unmute():
    print("unmute")
    global sdk
    sdk.unmute()


def on_started():
    print("on_started")
    global is_started
    is_started = True

    global check_sensor
    check_sensor = True

    # for debug
    time.sleep(1)
    sensorDetected()


    return


def on_failed(ecode, failstr):
    print("on_failed : %s(%d)" % (failstr, ecode))
    return


def on_stop():
    print("on_stop")
    return


def on_text_out(data):
    print("on_text_out", data)
    return


def on_meta_out(data):
    print("on_meta_out", data)
    metadict = json.loads(data)
    print(metadict)
    try:
        if metadict["type"] == "nlu_result" and metadict["version"] == "sebastien-1.0.0":
            if "systemText" in metadict:
                text = metadict["systemText"]["expression"]
                print("text:", text, text == "山", text == "合言葉が認証されました")
                if text == "山":
                    global mute_after_play
                    mute_after_play = False
                    global sdk
                    sdk.unmute()
                elif text == "合言葉が認証されました":
                    openDoor()
                    global check_sensor
                    check_sensor = True
    except Exception as e:
       print(e)
    return


def on_play_start(data):
    print("on_play_start", data)
    return


def on_play_end(data):
    # 音声再生が終わったら、wake up wordを待機するためにSebastienの音声入力をOFFにする
    print("on_play_end", data)
    global sdk
    global mute_after_play
    if mute_after_play:
        sdk.mute()
    else:
        # 続けて音声を受け取る
        # その次の音声再生ではmute音声入力をoffにする
        mute_after_play = True
    return


def on_cache_failed():
    print("on_cache_failed")
    return


def on_gain_value(data):
    print("on_gain_value", data)
    return


def cancel_play():
    print("cancel play")

    global sdk
    sdk.cancel_play()

    return


def init(configname=None):
    global sdk
    if configname is not None:
        sdk = speak.Speak(configname)
    else:
        sdk = speak.Speak()

    # 要初期化
    sdk.init()

    # コールバック先の設定
    sdk.set_on_meta_out(on_meta_out)
    sdk.set_on_text_out(on_text_out)
    sdk.set_on_cache_failed(on_cache_failed)
    sdk.set_on_gain_value(on_gain_value)
    sdk.set_on_play_start(on_play_start)
    sdk.set_on_play_end(on_play_end)

def start():
    sdk.start(on_started, on_failed, False)

def poll():
    if not is_started :
        return
    global sdk
    sdk.poll()

def sendAikotobaCommand():
    global sdk
    metaData = NluMetaData()
    metaData.cacheFlag = False
    metaData.voiceText = "合言葉"
    sdk.put_meta(metaData)

def openDoor():
    servo.start(0)
    servo.ChangeDutyCycle(2.5)
    time.sleep(4.0)
    servo.ChangeDutyCycle(7.25)
    time.sleep(1.0)
    servo.stop()

def sensorDetected(value):
    print("ON")
    global check_sensor
    check_sensor = False
    sendAikotobaCommand()

def tickSensor():
    try:
        if not check_sensor:
            return
        global sensor_buff
        
        data = i2c.read_word_data(sensor_addr, sensor_conf)
        raw = swap16(int(hex(data),16))
        raw_s = sign16(int(hex(raw),16))
        value = round((1 * raw_s / 32767),4)
        sensor_buff.append(value)
        if len(sensor_buff) > 30:
            max_value = max(sensor_buff)
            print(max_value)
            sensor_buff = []
            if(max_value > sensor_threshold) :
                sensorDetected(max_value)
    except Exception as e:
        print("sensor error:", e)
