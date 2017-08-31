#!/usr/bin/env python3
from __future__ import unicode_literals
import yt_downloader
import archive_uploader
import argparse

from youtube_dl.utils import DownloadError
import youtube_dl
import requests
import json
import ctypes
import os
import platform
import sys
import subprocess

from internetarchive import get_item, upload
from archive_uploader import ar_upload

from sys import stdout
from time import sleep

MIN_FREE_SPACE = 1590 # 1000Mb

def delete_none_completed_videos(ia_id):
    # import os
    dir = os.path.join('.', ia_id)
    files = os.listdir(dir)
    for file in files:
        if file.endswith(".part") or file.endswith(".part.aria2__temp"):
            os.remove(os.path.join(dir,file))

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('++++++Downloaded ' + d['filename'] + ' ++++++')

    # if d['status'] != 'downloading':
    #     stdout.write("\n")
    
    if d['status'] == 'downloading':
        txt = d['filename'] + d['_percent_str'] + ' || '+  d['_eta_str']
        stdout.write("\r%s" % txt)
        stdout.flush()
        sleep(1) # move the cursor to the next line

def download(url, identifier):
    ydl_opts = {
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format': '22',
        'external_downloader': 'aria2c',
        'download_archive': identifier + '.download-archive', 
        'outtmpl': identifier + '/%(upload_date)s-%(id)s-%(title)s__%(format_id)s.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('============================')
        print('Downloading Youtube videos...')
        ydl.download([url])


parser = argparse.ArgumentParser(description='Backup Youtube Channels to archive.org')
parser.add_argument('-u','--url', help='Url of Youtube channel or playlist.', required=True)
parser.add_argument('-i','--identifier', help='Identifier for archive.org page.', required=True)
args = vars(parser.parse_args())
yt_url = args['url']
ia_id = args['identifier']

try:
    delete_none_completed_videos(ia_id)
except:
    pass

if archive_uploader.create_identifier(ia_id):
    # yt_downloader.yt_archiver(yt_url, ia_id)
    while True:
        try:
            download(yt_url, ia_id)
            print('===Finished Downloading, Uploading...')
            delete_none_completed_videos(ia_id)
            ar_upload(ia_id, ia_id)
            break
        except DownloadError:
            print('=======Disk Full, Uploading to free space...')
            delete_none_completed_videos(ia_id)
            ar_upload(ia_id, ia_id)

        except:
            print("Download err")
            break
else:
    print('Identifier Not available please choose another one.')

