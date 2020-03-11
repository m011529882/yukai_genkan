# coding:utf-8
import time

def loop():
	start = time.time()

	while True:
   		time.sleep(1)
   		if time.time() - start > 50:
   			print('!!BREAK!!')
   			break