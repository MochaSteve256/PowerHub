from gc import callbacks
import watchpoints
import time

def _callback(frame, elem, exec_info):
    print('callback')
    while True:
        time.sleep(1)
        print('skibidi' + str(x))

x = 1

watchpoints.watch(x, callback=_callback)

while True:
    x += 1
    time.sleep(5)