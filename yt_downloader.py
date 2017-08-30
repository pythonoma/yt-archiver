#!/usr/bin/env python3
from __future__ import unicode_literals
import youtube_dl
import requests

import ctypes
import os
import platform
import sys

from internetarchive import get_item, upload
from archive_uploader import ar_upload

from sys import stdout
from time import sleep

MIN_FREE_SPACE = 1590 # 1000Mb


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    # if d['status'] == 'finished':
    #     print('Done downloading ...')

    if d['status'] != 'downloading':
        stdout.write("\n")
    
    if d['status'] == 'downloading':
        txt = d['filename'] + d['_percent_str'] + ' || '+  d['_eta_str']
        stdout.write("\r%s" % txt)
        stdout.flush()
        sleep(1) # move the cursor to the next line

def yt_archiver(url, identifier):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # 'format': '18',
        'external_downloader': 'aria2c',
        'outtmpl': identifier + '/%(upload_date)s-%(title)s.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('============================')
        print('Getting Youtube video links...')
        info = ydl.extract_info(url, download=False)
        video_entries = info['entries']
        video_entries_len = len(video_entries)

        # Cycle though videos & download them
        for index, ve in enumerate(video_entries):
            video_url = ve['webpage_url']
            # print(get_free_space_mb('.'))
            if(get_free_space_mb('.') > MIN_FREE_SPACE):
                print( str(index+1) + '/' + str(video_entries_len) + ' Downloading: ' + ve['title'] + ' || '+ video_url)
                ydl.download([video_url])
            else:
                # Disk space nearly full, Upload & delete what was downloaded
                print('============================')
                print('Uploading...')
                ar_upload(identifier, files_folder=identifier, auto_delete=True)
        
        # Upload if downloaded_size > MIN_FREE_SPACE or residual files from cycles
        print('============================')
        print('Uploading...')
        ar_upload(identifier, files_folder=identifier ,auto_delete=True)




def get_free_space_mb(dirname):
    """Return folder/drive free space (in megabytes)."""
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dirname), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024
    else:
        st = os.statvfs(dirname)
        return st.f_bavail * st.f_frsize / 1024 / 1024
def get_video_info(url):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # 'postprocessors': [{
        #     'key': 'FFmpegExtractAudio',
        #     'preferredcodec': 'mp3',
        #     'preferredquality': '192',
        # }],
        'logger': MyLogger(),
        # 'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # ydl.download(['https://www.youtube.com/watch?v=BaW_jenozKc'])
        formats = info['formats']
        # print(formats)
        """
        18 - 640x360 (medium)
        22 - 1280x720 (hd720)
        """
        # td_formats = ['18', '22']
        for f in formats:
            # if f['format_id'] in td_formats:
            #     print(f['format'] + ' ' + size_formater(get_file_size_from_url(f['url'])))
            if f['ext'] == 'mp4':
                try:
                    print( f['format'] +  str(size_formater(f['filesize'])))
                except:
                    print(f['format'] + ' ' + size_formater(get_file_size_from_url(f['url'])))

def get_file_size_from_url(url):
    response = requests.head(url, allow_redirects=True)
    size = response.headers.get('content-length', 0)
    return size

def size_formater(bytes):
    # number of bytes in a megabyte
    MBFACTOR = float(1 << 20)
    return ('{:<1}: {:.2f} MB'.format('', int(bytes) / MBFACTOR))
