# coding:utf-8
import sys
import RPi.GPIO as GPIO
import sebastien
import time

# 定数値

# 設定ファイル
CONFIGNAME = "../config.json"

# codamaのwake up wordが検出されるとhighになるGPIOの番号
CODAMA_TRIGGERD_GPIO = 27

def detected(value):
    # wake up wordを検出したら、Sebastienの音声入力をONにする
    print ("detected wake-up-word")
    sebastien.unmute()


def cleanup():
    print ("cleanup")
    GPIO.cleanup()


def codama_setup():
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(CODAMA_TRIGGERD_GPIO, GPIO.IN)

    GPIO.add_event_detect(CODAMA_TRIGGERD_GPIO, GPIO.RISING, callback=detected)


if __name__ == "__main__":
    try:
        codama_setup()

        sebastien.init(CONFIGNAME)
        print("start")
        sebastien.start()
        print("started")
        count = 0
        while True:
            sebastien.tickSensor()
            time.sleep(0.03)
            count += 1
            if count >70 :
                print("poll")
                sebastien.poll()
                count = 0
    except Exception as e:
        print(e)
        cleanup()
        exit(0)
