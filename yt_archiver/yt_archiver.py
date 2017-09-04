#!/usr/bin/env python3
from __future__ import unicode_literals
import argparse

from youtube_dl.utils import DownloadError
from internetarchive import get_item, upload, get_files
from internetarchive import delete as archive_delete

import youtube_dl
import os
import sys

import threading

# from archive_uploader import upload_to_archive

from sys import stdout
from time import sleep, strftime, gmtime
from datetime import datetime, timedelta

is_finished_downloading = False
is_uploading = False

bypass_long_filename = False
finished_downloading_first_video = False

downloaded_count = 0
total_downloads_count = 0
cur_video_id = ''

uploaded_count = 0
failed_download_list = []
failed_upload_list = []

time_started = datetime.now()


def chop_microseconds(delta):
    return delta - timedelta(microseconds=delta.microseconds)


def get_time_diff(start_time, end_time):
    delta_time = end_time - start_time
    return chop_microseconds(delta_time)


def is_downloads_path_empty(downloads_path):
    if os.path.exists(downloads_path):
        files = os.listdir(downloads_path)
        for file in files:
            if file.endswith(".mp4") or file.endswith(".webm") or \
                file.endswith(".3gp") or file.endswith(".flv") or \
                    file.endswith(".mp3") or file.endswith(".m4a"):
                return False
        return True
    else:
        return True


def print_status_string(ia_id, downloads_path):
    global is_finished_downloading
    while not is_finished_downloading or not is_downloads_path_empty(downloads_path):
        sleep(20)
        global uploaded_count, failed_upload_list, downloaded_count, failed_download_list, total_downloads_count
        successful_downloads = downloaded_count - len(failed_download_list)
        successful_uploads = uploaded_count - len(failed_upload_list)
        failed_downloads_file = os.path.join('downloads', ia_id + '.failed_downloads')
        failed_uploads_file = os.path.join('downloads', ia_id + '.failed_uploads')
        
        # with open( failed_downloads_file, 'w') as f:
        #     for v in failed_download_list:
        #         f.write(v + '\n')
        
        # with open( failed_uploads_file, 'w') as f:
        #     for v in failed_upload_list:
        #         f.write(v + '\n')
        
        to_upload_count = 0
        if os.path.exists(downloads_path):
            files = os.listdir(downloads_path)
            for file in files:
                if file.endswith(".mp4") or file.endswith(".webm") or \
                    file.endswith(".3gp") or file.endswith(".flv") or \
                        file.endswith(".mp3") or file.endswith(".m4a"):
                    to_upload_count += 1
        

        status_string = '\n\n\n///////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\\' + \
                        '\n                            Backup Summary   ' + \
                        '\n                         ' + strftime("%Y-%m-%d %H:%M:%S", gmtime())  + \
                        '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' + \
                        '\n>>>>>>>>>>> Downloaded: ' + str(successful_downloads) + '/' + str(total_downloads_count) + ',  ' + \
                        str(len(failed_download_list)) + ' Failed.     <<<<<<<' + \
                        '\n>>>>>>>>>>> Uploaded  : ' + str(successful_uploads)  + ',    ' + str(to_upload_count) + ' Pending.    <<<<<<<' + \
                        '\n\\\\\\\\\\\\\\\\\\\\\\\\\\\////////////////////////////////////////////////\n\n\n'
                        # 'Failed download list saved to "' + str(failed_downloads_file) + ' .\n' + \
                        # 'Failed upload list saved to "' + str(failed_uploads_file) + ' .\n' + \
                        
        stdout.write(status_string)
        sleep(5)


def get_ia_item_files_count(ia_id, formats=['WebM', 'MPEG4', '3GP']):
    return len(list(get_files(ia_id, formats=formats)))


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
        print('Identifier available.')
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


class MyYoutubeDLM(youtube_dl.YoutubeDL):

    def prepare_filename(self, info_dict):
        sanitized_path = super(MyYoutubeDLM, self).prepare_filename(info_dict)
        short_sanitized_path = self.restrict_file_name_length(sanitized_path)
        return short_sanitized_path


    def restrict_file_name_length(self, sanitized_path):
        filename_with_ext = os.path.basename(sanitized_path)
        filename_without_ext = os.path.splitext(filename_with_ext)[0]
        ext = os.path.splitext(filename_with_ext)[1]

        filename_encoded = filename_without_ext.encode('utf-8')
        
        filename_encoded_short = filename_encoded[:240]
        filename_decoded_short = filename_encoded_short.decode('utf-8', errors='replace') + ext

        short_sanitized_path = os.path.join(os.path.dirname(sanitized_path), filename_decoded_short)
        return short_sanitized_path


class MyLogger(object):
    # '[download] Downloading video 2174 of 4862'
    downloading_string = '[download] Downloading video '
    of_string = ' of '

    # '[youtube] ZdFnQwKTdiE: Downloading MPD manifest'
    downloading_webpage_string = ': Downloading MPD manifest'
    string_befor_video_id = '[youtube] '

    def debug(self, msg):
        global downloaded_count, total_downloads_count
        msg = str(msg)
        # print('===Debug: ' + msg)

        downloaded_string_start = msg.find(self.downloading_string)
        downloading_webpage_start = msg.find(self.downloading_webpage_string)

        if downloaded_string_start > -1:
            downloaded_number_start = downloaded_string_start + len(self.downloading_string)
            of_string_start = msg.find(self.of_string)
            downloaded_number = msg[downloaded_number_start:of_string_start]

            total_number_start = of_string_start + len(self.of_string)
            total_number = msg[total_number_start:]

            # print('Already Downloaded: ' + downloaded_number + '/' + total_number)
            downloaded_count = int(downloaded_number)
            total_downloads_count = int(total_number)
        # 'errorCode=3 Resource not found'
        elif downloading_webpage_start > -1:
            global cur_video_id
            cur_video_id_start = msg.find(self.string_befor_video_id) + len(self.string_befor_video_id)
            cur_video_id = msg[cur_video_id_start:downloading_webpage_start]
            print('current video: https://youtu.be/' + cur_video_id)


    def warning(self, msg):
        pass

    def error(self, msg):
        print('=-=- Error: "' + str(msg) + '"')


def my_hook(d):
    if d['status'] == 'finished':
        print('*************************************************************')
        print('=>>> Downloaded ' + d['filename'])
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        global downloaded_count 
        downloaded_count +=1
            
    if d['status'] == 'error':
        global failed_download_list
        failed_download_list.append(d['filename'])

    # if d['status'] != 'downloading':
    #     stdout.write("\n")
    
    if d['status'] == 'downloading':
        txt = d['filename'] + d['_percent_str'] + ' || ' + d['_eta_str']
        stdout.write("\r%s" % txt)
        stdout.flush()
        sleep(1) # move the cursor to the next line


def upload_downloaded_thread(ia_id, downloads_path):
    global is_finished_downloading, is_uploading, uploaded_count 
    
    uploaded_count = get_ia_item_files_count(ia_id)

    while not is_finished_downloading or not is_downloads_path_empty(downloads_path):
        sleep(10)
        # stdout.write('\n=================is_uploading: ' + str(is_uploading))        
        if is_uploading:
            pass
            # stdout.write('\n')
            # print('=====uploading, skipping check')
        else:
            # stdout.write('\n')
            # print('=====Upload thread checking:' + downloads_path)
            item = get_item(ia_id)
            md = dict(mediatype='movies',)

            if os.path.exists(downloads_path):
                files = os.listdir(downloads_path)
                for file in files:
                    if file.endswith(".mp4") or file.endswith(".webm") or \
                        file.endswith(".3gp") or file.endswith(".flv") or \
                            file.endswith(".mp3") or file.endswith(".m4a"):
                        try:
                            filepath = os.path.join(downloads_path, file)
                            is_uploading = True
                            item.upload(filepath,  metadata=md, delete=True, checksum=True)
                            
                            stdout.write('\n')
                            print('**********************************************************')
                            print('uploaded: ' + str(file))
                            print('==========================================================')
                            uploaded_count += 1
                        except Exception as ex:
                            stdout.write('\n')
                            print('**********************************************************')                            
                            print(ex)
                            print('Failed to upload:' + str(file))
                            print('==========================================================')
                            global failed_upload_list 
                            failed_upload_list.append(filepath)
                is_uploading = False      
    else:
        global time_started
        print("\n\nFinished uploading in " + str(get_time_diff(time_started, datetime.now())) + \
              ". Item available at https://archive.org/details/" + ia_id)


def yt_archiver(url, identifier, hide_date=False, hide_id=True, hide_format=True, use_aria2c=True):
    """
    1. Download youtube playlist or channel from 'url' with 'best' quality using 'aria2c'.
    2. Upload downloaded videos to Archive.org 'identifier'

    Optional args:
    hide_date: Hide youtube video upload date from file name.    
    hide_id: Hide youtube video id from file name.   
    hide_format: Hide youtube video format from file name.   

    """
    downloads_path = os.path.join('./downloads', identifier)
    ydl_opts = {
        # 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'format': 'best',
        # 'format': 'worst',
        # 'ignoreerrors': 'True',
        'download_archive': downloads_path+ '.download-archive',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        # 'nocheckcertificate': True,  # Solve 'The TLS connection was non-properly terminated'
    }
    if use_aria2c:
        ydl_opts['external_downloader'] = 'aria2c'

    output_t = downloads_path + '/'
    if not hide_date:
        output_t += '%(upload_date)s-'

    output_t += '%(title)s'
    if not hide_id:
        output_t += '__%(id)s'
    if not hide_format:
        output_t += '__%(format_id)s'
    
    ydl_opts['outtmpl'] = output_t + '.%(ext)s'

    with MyYoutubeDLM(ydl_opts) as ydl:
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
    parser.add_argument('-hid','--hideid', help='Hide youtube video id from filename .', action='store_true', default=True)
    parser.add_argument('-hf','--hideformat', help='Hide youtube video format from filename .', action='store_true', default=True)

    args = vars(parser.parse_args())
    yt_url = args['url']
    ia_id = args['identifier']
    arg_hide_id = args['hideid']
    arg_hide_date = args['hidedate']
    arg_hide_format = args['hideformat']

    # delete_none_completed_videos(ia_id)

    downloads_folder = os.path.join('downloads', ia_id)
    if create_archive_identifier(ia_id):
        bg_upload_downloaded_thread = threading.Thread(target=upload_downloaded_thread, args=(ia_id, downloads_folder,))
        bg_upload_downloaded_thread.start()
        
        bg_print_status_string_thread = threading.Thread(target=print_status_string, args=(ia_id, downloads_folder,))
        bg_print_status_string_thread.start()

        while True:
            try:
                yt_archiver(yt_url, ia_id, hide_date=arg_hide_date, hide_id=arg_hide_id, hide_format=arg_hide_format)
                print('===Finished Downloading==========')
                global is_finished_downloading
                is_finished_downloading = True
                # No errors occurred during download, Upload them...
                # upload_to_archive(ia_id, downloads_folder)
                break
            except DownloadError as ex:
                print('=======Download Error')
                # print(ex)
                ex = str(ex)
                if ex.find('aria2c exited with code 9') > -1 :   
                    print('=======No Space left on disk, waiting 10 seconds for uploading to free space...')               
                    # upload_to_archive(ia_id, downloads_folder)
                    sleep(10)
                    continue
                
                elif ex.find('aria2c exited with code 2') > -1 :   
                    print('=======Connection timeout, Sleeping for 10 seconds and retrying...')               
                    sleep(10)
                    continue

                elif ex.find('aria2c exited with code 3') > -1:
                    global cur_video_id
                    print('=======Resource Not Found, Downloading video https://youtu.be/' + cur_video_id + ' without aria2.')
                    yt_archiver('https://youtu.be/'+str(cur_video_id), ia_id, hide_date=arg_hide_date, hide_id=arg_hide_id,
                                hide_format=arg_hide_format, use_aria2c=False)
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
                    print('=======file I/O error occurred, sleeping 10 seconds.....')
                    # upload_to_archive(ia_id, downloads_folder)
                    sleep(10)
                    exit


                elif ex.find('aria2c exited with code 18') > -1 :   
                    print('=======aria2 could not create directory.....')
                    exit 
                
                elif ex.find('aria2c exited with code 1') > -1 :   
                    print('=======Unknown error occcured, Sleeping for 10 seconds...')               
                    sleep(10)
                    # upload_to_archive(ia_id, downloads_folder)
                    continue
                    
                elif ex.find('account associated with this video has been terminated') > -1 or \
                        ex.find('blocked it on copyright grounds') > -1 or\
                            ex.find('blocked') > -1:
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
