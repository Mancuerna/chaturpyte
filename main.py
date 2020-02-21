from Chaturbate import Chaturbate
import queue
import threading
import colorama
import time
import datetime
import os

colorama.init(strip=False)

MODELS = queue.Queue()
ACTIVE_RECORDINGS = []
PATH = os.path.dirname(os.path.abspath(__file__))


def get_model_list():
    [MODELS.put(model.strip()) for model in open(f'{PATH}/model_list.txt', 'r').readlines()]


def get_active_recordings():
    global ACTIVE_RECORDINGS
    ACTIVE_RECORDINGS = [t.getName() for t in threading.enumerate()]


def record_models():
    while MODELS.empty() is False:
        model = MODELS.get()
        if model not in ACTIVE_RECORDINGS:
            ch = Chaturbate(model, PATH)
            if ch.online_status() is False:
                print(f'{model}: model {colorama.Fore.RED}not online.{colorama.Style.RESET_ALL}')
            else:
                threading.Thread(target=ch.save_stream, name=model).start()


def main():
    while True:
        print(f'\n{datetime.datetime.now():%Y/%m/%d %H:%M:%S}')
        get_model_list()
        record_models()
        get_active_recordings()
        time.sleep(360)


if __name__ == "__main__":
    main()
