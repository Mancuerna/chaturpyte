import ffmpeg
import datetime
from  colorama import Fore, Style
import requests
from pathlib import Path
import threading


class Chaturbate:
    def __init__(self, user_slug, path):
        self.r_user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}
        self.user_slug = user_slug
        self.user_stream = ''
        self._get_streams()
        self.save_path = f'{path}/recordings/{self.user_slug}/{datetime.datetime.now().strftime("%B")}'
        self.output_stream = None

    def online_status(self):
        return self.user_stream

    def _get_streams(self):
        stream_source = requests.get(f'https://chaturbate.com/api/chatvideocontext/{self.user_slug}/', headers=self.r_user_agent).json()[
            'hls_source']
        if stream_source:
            self.user_stream = stream_source
        else:
            self.user_stream = False

    def _ensure_dir(self):
        Path(self.save_path).mkdir(parents=True, exist_ok=True)

    def save_stream(self):
        self._ensure_dir()
        self.output_stream = f'{self.save_path}/{self.user_slug}_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.mp4'
        stream = ffmpeg.input(self.user_stream)
        stream = ffmpeg.output(stream, self.output_stream, c='copy', f='mp4', loglevel='quiet')
        try:
            print(f'{Fore.GREEN}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.GREEN} Online{Style.RESET_ALL} Start Recording..')
            ffmpeg.run(stream)
        except:
            print(f'{Fore.RED}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.RED}\u25FC {Fore.WHITE}Recording  Stopped (not online or private show).')
        finally:
            #print(threading.currentThread().getName())
            print(f'{Fore.RED}\u2190 {Fore.WHITE}{self.user_slug}:{Fore.CYAN}\u25FC {Fore.WHITE}Recording{Style.RESET_ALL} Stopped')
            print(f'{Fore.RED}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.RED} Offline.{Style.RESET_ALL}')

