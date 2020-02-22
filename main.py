from Chaturbate import Chaturbate
import queue
import threading
import colorama 
from colorama import Fore, Style
import time
import datetime
import os
from pathlib import Path

colorama.init(strip=False)

MODELS = queue.Queue()
ACTIVE_RECORDINGS = []
PATH = os.path.dirname(os.path.abspath(__file__))
FILES = {}

def get_model_list():
    [MODELS.put(model.strip()) for model in open(f'{PATH}/model_list.txt', 'r').readlines()]


def get_active_recordings():
    global ACTIVE_RECORDINGS
    ACTIVE_RECORDINGS = [t.getName() for t in threading.enumerate()]
    if ACTIVE_RECORDINGS[1::]:
        for arco in ACTIVE_RECORDINGS[1::]:
            file_size = str(round(get_file_size(FILES[arco][0]), 2))
            start_at = FILES[arco][1].strftime("%H:%M:%S %m-%d-%Y")
            duration = current_stream_duration(FILES[arco][1])                
            print(f'{Fore.GREEN}\u25FC {Fore.WHITE}{arco}:{Fore.GREEN} Online {Fore.RED}\u25B6 {Fore.WHITE}Recording.. {file_size}Gb {duration}min start {start_at}')
            
            
def get_file_size(file):
    while True:
        try:
            return Path(file).stat().st_size/(1024*1024*1024)
            break
        except FileNotFoundError:
            time.sleep(0.1)

def current_stream_duration(start_time):
    return str(round((datetime.datetime.now()-start_time).seconds/60, 2))
            

def record_models():
    while MODELS.empty() is False:
        model = MODELS.get()
        if model not in ACTIVE_RECORDINGS:
            ch = Chaturbate(model, PATH)
            if ch.online_status() is False:
                print(f'{Fore.RED}\u25CF {Fore.WHITE}{model}:{Fore.RED} Offline.{Style.RESET_ALL}')
            else:
                threading.Thread(target=ch.save_stream, name=model).start()
                while not ch.output_stream:
                    time.sleep(0.1)
                FILES[model] = [ch.output_stream, datetime.datetime.now()]
                
def main():
    while True:
        print(f'\n{datetime.datetime.now():%Y/%m/%d %H:%M:%S}')
        get_model_list()
        record_models()
        get_active_recordings()
        time.sleep(360)

if __name__ == "__main__":
    main()
