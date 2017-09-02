#!/usr/bin/env python3
from __future__ import unicode_literals
import argparse

from youtube_dl.utils import DownloadError
from internetarchive import get_item, upload
from internetarchive import delete as archive_delete

import youtube_dl
import os
import sys

# from archive_uploader import upload_to_archive

from sys import stdout
from time import sleep


def create_archive_identifier( identifier):
    """
    Creates Archive.org identifier & Tests uploading to it with '__.test' file.

    Returns:
    True: if created successfully.
    False: if Can't be created.
    """

    print('============================')
    print('Checking if Archive.org identifier available...')
    item = get_item(identifier)
    # print(dir(item))
    create_test_file()
    md = dict(mediatype='movies',)
    try:
        item.upload('__.test', metadata=md, delete=True)
        item.modify_metadata(md)
        archive_delete(identifier, files='__.test')
        print('Identifier created.')
        return True
    except Exception as ex:
        print(ex)
        return False
    
def create_test_file():
    """
    Creates a local '__.test' file.
    """
    try:
        with open('__.test','w') as f:
            f.write('Test File')
    except Exception as ex:
        print(ex)
        print('Failed to create test file at archive.org.')

def upload_to_archive(identifier, files_folder, auto_delete=True, verbose=True):
    """
    Upload files in 'files_folder' to Archive.org 'identifier' with metadata='movies'.

    Optional args:
    auto_delete: auto delete uploaded files after verifying they are uploaded.
    verbose: display upload progress.
    """
    delete_none_completed_videos(identifier)

    item = get_item(identifier)
    md = dict(mediatype='movies',)
    try:
        item.upload(files_folder+'/', metadata=md, delete=auto_delete, verbose=verbose, checksum=True)
        print("Finished uploading. Item available at https://archive.org/details/" + identifier)
    except Exception as ex:
        print(ex)
        print('Error Uploading')


def delete_none_completed_videos(ia_id):
    """
    Delete none completed videos generated by aria2c; to avoid uploading them.
    """
    video_ext_list = ['.mp4', '.webm', '.3gp', '.flv', '.mp3', '.m4a']

    dir = os.path.join('downloads', ia_id)
    if os.path.exists(dir):
        files = os.listdir(dir)
        for file in files:
            if not file.endswith(".mp4") and not file.endswith(".webm") and \
                    not file.endswith(".3gp") and not file.endswith(".flv") and \
                    not file.endswith(".mp3") and not file.endswith(".m4a"):
                try:
                    os.remove(os.path.join(dir,file))
                    print('removed: ' + str(file))
                except Exception as ex:
                    print(ex)
                    print('Failed to remove none completed video files.')

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('+Downloaded ' + d['filename'])
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    # if d['status'] != 'downloading':
    #     stdout.write("\n")
    
    if d['status'] == 'downloading':
        txt = d['filename'] + d['_percent_str'] + ' || '+  d['_eta_str']
        stdout.write("\r%s" % txt)
        stdout.flush()
        sleep(1) # move the cursor to the next line

def yt_archiver(url, identifier, hide_date=False, hide_id=False, hide_format=False):
    """
    1. Download youtube playlist or channel from 'url' with 'best' quality using 'aria2c'.
    2. Upload downloaded videos to Archive.org 'identifier'

    Optional args:
    hide_date: Hide youtube video upload date from file name.    
    hide_id: Hide youtube video id from file name.   
    hide_format: Hide youtube video format from file name.   

    """
    ydl_opts = {
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format': 'best',
        # 'format': 'worst',
        # 'ignoreerrors': 'True',
        'external_downloader': 'aria2c',
        'download_archive': os.path.join('downloads', identifier+ '.download-archive') , 
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    output_t = os.path.join('downloads', identifier) + '/'
    if not hide_date:
        output_t += '%(upload_date)s-'
    output_t += '%(title)s'
    if not hide_id:
        output_t += '__%(id)s'
    if not hide_format:
        output_t += '__%(format_id)s'
    
    ydl_opts['outtmpl'] = output_t + '.%(ext)s'

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('============================')
        print('Downloading Youtube videos...')
        ydl.download([url])

def skip_yt_video(video_id, identifier):
    print("Skipping "+ video_id)
    with open(os.path.join('downloads', identifier+ '.download-archive'), 'a') as f:
        f.write('youtube '+ video_id +'\n')

def main():
    parser = argparse.ArgumentParser(description='Backup Youtube Channels to archive.org')
    parser.add_argument('-u','--url', help='Url of Youtube channel or playlist.', required=True)
    parser.add_argument('-i','--identifier', help='Identifier for archive.org page.', required=True)
    parser.add_argument('-hd','--hidedate', help='Hide youtube video upload date from filename .', action='store_true', default=False)
    parser.add_argument('-hid','--hideid', help='Hide youtube video id from filename .', action='store_true', default=False)
    parser.add_argument('-hf','--hideformat', help='Hide youtube video format from filename .', action='store_true', default=False)

    args = vars(parser.parse_args())
    yt_url = args['url']
    ia_id = args['identifier']
    arg_hide_id = args['hideid']
    arg_hide_date = args['hidedate']
    arg_hide_format = args['hideformat']

    delete_none_completed_videos(ia_id)

    downloads_folder = os.path.join('downloads', ia_id)
    if create_archive_identifier(ia_id):
        while True:
            try:
                yt_archiver(yt_url, ia_id, hide_date=arg_hide_date, hide_id=arg_hide_id, hide_format=arg_hide_format)
                print('===Finished Downloading, Uploading to "' + ia_id +'"')
                # No errors occured during download, Upload them...
                upload_to_archive(ia_id, downloads_folder)
                break
            except DownloadError as ex:
                print('=======Download Error')
                # print(ex)
                ex = str(ex)
                if ex.find('aria2c exited with code 9') > -1 :   
                    print('=======No Space left on disk, uploading to free space...')               
                    upload_to_archive(ia_id, downloads_folder)
                    continue
                elif ex.find('aria2c exited with code 1') > -1 :   
                    print('=======Unknown error occcured, Sleeping for 10 seconds and retrying...')               
                    sleep(10)
                    continue
                
                elif ex.find('aria2c exited with code 2') > -1 :   
                    print('=======Connection timeout, Sleeping for 10 seconds and retrying...')               
                    sleep(10)
                    continue

                elif ex.find('aria2c exited with code 6') > -1 :   
                    print('=======Network proplem, Sleeping for 10 seconds and retrying...')               
                    sleep(10)
                    continue

                elif ex.find('aria2c exited with code 15') > -1 :   
                    print('=======Couldnot open existing file...')
                    exit 

                elif ex.find('aria2c exited with code 16') > -1 :   
                    print('=======could not create new file or truncate existing file....')
                    exit 
                
                elif ex.find('aria2c exited with code 17') > -1 :   
                    print('=======file I/O error occurred.....')
                    upload_to_archive(ia_id, downloads_folder)

                elif ex.find('aria2c exited with code 18') > -1 :   
                    print('=======aria2 could not create directory.....')
                    exit 
                    
                elif ex.find('account associated with this video has been terminated') > -1 or \
                        ex.find('blocked it on copyright grounds') > -1:
                    video_id_start = ex.find(":") +6
                    video_id_end = ex.find(":", video_id_start)
                    video_id = ex[video_id_start:video_id_end]
                    if video_id != '':
                        skip_yt_video(video_id, ia_id)
                        continue
                else:
                    print(ex)
                    exit
                # elif ex.find('')
            # except OSError as ex:
            #     if ex.errno is 28:
            #         print('No space left on disk, uploading')
            #         exit
            except Exception as ex:
                print(ex)
                print("Download error occured...")
                break
                
    else:
        print('Identifier Not available please choose another one.')



if __name__ == "__main__":
    main()
