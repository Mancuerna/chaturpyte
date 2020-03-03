import ffmpeg
import datetime
from  colorama import Fore, Style
import requests
from pathlib import Path
import threading 
import time
import json

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0'}

class Chaturbate(threading.Thread):
    def __init__(self, user_slug, path, time_format):
        threading.Thread.__init__(self)
        self.threadingID = self.user_slug = user_slug
        self.save_path = f'{path}/recordings/{self.user_slug}/{datetime.datetime.now().strftime("%B")}'
        self.user_stream = ''
        self.output_stream = False
        self.status = None
        self.process = None
        self.start_recording = ''
        self.time_format = time_format
        self.errors = None
    
    def run(self):
        while not self.status and not self.errors:
            self._get_streams()
        if self.errors:
            print(f'{Fore.RED}\u25CF ERROR {Fore.WHITE}{self.user_slug}:{Fore.RED}{self.errors}{Style.RESET_ALL}')
        elif self.status == 'public':
            print(f'{Fore.GREEN}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.GREEN} Now Connected! {Fore.YELLOW}start Recording{Style.RESET_ALL}')
            self._save_stream()
            print(f'{Fore.RED}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.RED} Offline.{Style.RESET_ALL}')
        elif self.status == 'offline':
            print(f'{Fore.RED}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.RED} Offline.{Style.RESET_ALL}')
            self.status = 'offline'
        elif self.status == 'unauthorized':
            print(f'{Fore.GREEN}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.GREEN} Online {Fore.YELLOW} Private {Style.RESET_ALL}')
            self.status = 'offline'

    def _current_file_size(self):
        while True:
            try:
                return round(Path(self.output_stream).stat().st_size/(1024*1024*1024), 2)
            except FileNotFoundError:
                time.sleep(0.1)

    def _current_stream_duration(self):
        return str(round((datetime.datetime.now()-self.start_recording).seconds/60, 2))

    def _get_streams(self):
        try:
            r = requests.get(f'https://chaturbate.com/api/chatvideocontext/{self.user_slug}/', headers=HEADERS)
            r.raise_for_status()
            stream_source = r.json()
            if 'code' in stream_source and stream_source['code'] == 'unauthorized':
                self.status = 'unauthorized'
            else:
                room_status = stream_source['room_status']
                hls_source = stream_source['hls_source']
            if hls_source:
                self.status = room_status
                self.user_stream = hls_source
            else:
                self.status = room_status
        except json.JSONDecodeError:
            self.errors = 'captcha'
        except requests.exceptions.HTTPError as http_err:
            self.errors = r.status_code
            
    def _ensure_dir(self):
        Path(self.save_path).mkdir(parents=True, exist_ok=True)

    def _save_stream(self):
        self._ensure_dir()
        self.output_stream = f'{self.save_path}/{self.user_slug}_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.mp4'
        self.process = (
            ffmpeg
            .input(self.user_stream)
            .output(self.output_stream, c='copy', f='mp4')
        )
        try:
            self.start_recording = datetime.datetime.now()
            self.process.run(quiet=True)
        except Exception as e:
            print(f'{Fore.RED}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.RED}\u25FC {Fore.WHITE}Recording  Stopped (not online or private show).')
        finally:
            print(f'{Fore.RED}\u2190 {Fore.WHITE}{self.user_slug}:{Fore.CYAN}\u25FC {Fore.WHITE}Recording{Style.RESET_ALL} Stopped')
            self.status = 'offline'
    
    def print_status(self):
        print(f'{Fore.GREEN}\u25CF {Fore.WHITE}{self.user_slug}:{Fore.GREEN} Online {Style.RESET_ALL}')
        print(f'{Fore.GREEN}  \u21B3{Fore.WHITE}Recording{Fore.RED} \u25B6 {Fore.WHITE}{self._current_file_size()}Gb {self._current_stream_duration()}min start {self.start_recording.strftime(self.time_format)}')
        
