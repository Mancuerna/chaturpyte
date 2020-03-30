from Chaturbate import Chaturbate
import queue
import colorama
from colorama import Fore, Style
import time
import datetime
import os
import threading
import sys

MODELS = queue.Queue()
PATH = os.path.dirname(os.path.abspath(__file__))
ACTIVE_FAKE = {}
TIME_FORMAT = '%H:%M:%S %m-%d-%Y'
TICKS = 360

colorama.init(strip=False)

def waiting_captcha_reset():
    waiting_time = 0
    print(f'{Fore.RED}\u2620 {Fore.WHITE} Captcha error, waiting for response..')
    while waiting_time < 600:
        time.sleep(1)
        waiting_time+=1
        

def manager():
    [MODELS.put(model.strip()) for model in open(f'{PATH}/model_list.txt', 'r').readlines()]
    while MODELS.empty() is False:
        model = MODELS.get()
        if model in ACTIVE_FAKE and ACTIVE_FAKE[model].isAlive() is False:
            ACTIVE_FAKE.pop(model, None)
        if model in ACTIVE_FAKE and ACTIVE_FAKE[model].isAlive() is True:
            ACTIVE_FAKE[model].print_status()
        if model not in ACTIVE_FAKE:
            ch = Chaturbate(model, PATH, TIME_FORMAT)
            ch.start()
            while not ch.status and not ch.errors:
                time.sleep(0.1)
            if ch.status == 'offline':
                ch.join()
            elif ch.status == 'public' and model not in ACTIVE_FAKE:
                ACTIVE_FAKE[ch.threadingID] = ch
            elif ch.errors:
                if ch.errors == 'captcha':
                    waiting_captcha_reset()

def main():
    try:
        while True:
            print(f'{Fore.BLUE}\u267B {Fore.WHITE}{datetime.datetime.now().strftime(TIME_FORMAT)}')
            manager()
            print (f'Current Cams {threading.active_count()-1}')
            time.sleep(TICKS)
    except KeyboardInterrupt:
        for t in ACTIVE_FAKE:
            ACTIVE_FAKE[t].stop()
        print(f'{Fore.YELLOW}bye{Style.RESET_ALL}')
        sys.exit(0)

if __name__ == "__main__":
    main()
