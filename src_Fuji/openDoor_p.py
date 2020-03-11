import pigpio
import time
import subprocess
import signal
import sys

pin=4
pi = pigpio.pi()
pi.set_servo_pulsewidth(pin, 1500)


def res_cmd(cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).communicate()[0]

def main():
        current_angle = 90
        cmd = ("/home/pi/codama/codama-doc/utils/./codama_i2c DOAANGLE")
        while True:
                n=20
                i=0
                value = res_cmd(cmd).strip()
                target_angle = int(value.strip("DOAANGLE:"))
                if target_angle < 30 or target_angle > 150:
                        target_angle = 90
				print 'Target angle:' + str(target_angle)
                divided_angle = (current_angle - target_angle)/n
                while i<n:
                        current_angle -= divided_angle;
                        pi.set_servo_pulsewidth(pin, (85/9)*current_angle + 650)
                        time.sleep(0.05)
                        i+=1
                time.sleep(0.5)

if __name__ == '__main__':
  main()