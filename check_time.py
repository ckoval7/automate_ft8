import sys
import time

try:
    cycle = sys.argv[1]
except:
    cycle = 'even'

def check_time(cycle):
    now = time.localtime().tm_sec
    if cycle == 'odd':
        if now < 15:
            print("Waiting for 15 second mark...")
            time.sleep(14-now)
        elif now >= 45:
            print("Waiting for new minute...")
            time.sleep(16)
            check_time('odd')
        else:
            print("Waiting for 45 second mark...")
            time.sleep(45 - now)
    else:
        if now < 30:
            print("Waiting for 30 second mark")
            time.sleep(29-now)
        else:
            print("Waiting for the top of the minute...")
            time.sleep(59 - now)

check_time(cycle)
