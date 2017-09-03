#!/usr/bin/env python3
from __future__ import unicode_literals
import argparse

from youtube_dl.utils import DownloadError
from internetarchive import get_item, upload
from internetarchive import delete as archive_delete

import youtube_dl
import os
import sys

import threading

# from archive_uploader import upload_to_archive

from sys import stdout
from time import sleep, strftime, gmtime

is_finished_downloading = False
is_uploading = False

bypass_long_filename = False
finished_downloading_first_video = False

downloaded_count = 0
uploaded_count = 0
failed_download_list = []
failed_upload_list = []

# cwd = os.getcwd()

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
        global uploaded_count, failed_upload_list, downloaded_count, failed_download_list
        successful_downloads = downloaded_count - len(failed_download_list)
        successful_uploads = uploaded_count - len(failed_upload_list)
        failed_downloads_file = os.path.join('downloads', ia_id + '.failed_downloads')
        failed_uploads_file = os.path.join('downloads', ia_id + '.failed_uploads')
        
        with open( failed_downloads_file, 'w') as f:
            for v in failed_download_list:
                f.write(v + '\n')
        
        with open( failed_uploads_file, 'w') as f:
            for v in failed_upload_list:
                f.write(v + '\n')
        
        to_upload_count = 0
        if os.path.exists(downloads_path):
            files = os.listdir(downloads_path)
            for file in files:
                if file.endswith(".mp4") or file.endswith(".webm") or \
                    file.endswith(".3gp") or file.endswith(".flv") or \
                        file.endswith(".mp3") or file.endswith(".m4a"):
                    to_upload_count += 1
        


        status_string = '\n\n\n///////////////////////////////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\' + \
                        '\n                                           Backup Summary                                               ' + \
                        '\n                                   ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + '                      ' + \
                        '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~' + \
                        '\n>>>>>>>>>>> Successfuly downloaded: ' + str(successful_downloads) + '/' + str(downloaded_count) + ',  ' + \
                        'Failed: ' + str(len(failed_download_list)) + '. <<<<<<<<<<<' + \
                        '\n>>>>>>>>>>> Successfuly uploaded: ' + str(successful_uploads)  + ' videos. <<<<<<<<<<<' + \
                        '\n>>>>>>>>>>> To upload: ' + str(to_upload_count) + '\n' + \
                        '\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\/////////////////////////////////////////////////////\n\n\n'
                        # 'Failed download list saved to "' + str(failed_downloads_file) + ' .\n' + \
                        # 'Failed upload list saved to "' + str(failed_uploads_file) + ' .\n' + \
                        
        stdout.write(status_string)
        


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
        filename_encoded_short = filename_encoded[:245]
        filename_decoded_short = filename_encoded_short.decode('utf-8') + ext

        short_sanitized_path = os.path.join(os.path.dirname(sanitized_path), filename_decoded_short)
        return short_sanitized_path



class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


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
    global is_finished_downloading, is_uploading

    while not is_finished_downloading or not is_downloads_path_empty(downloads_path):
        sleep(10)
        # stdout.write('\n=================is_uploading: ' + str(is_uploading))        
        if is_uploading:
            # pass
            stdout.write('\n')
            print('=====uploading, skipping check')
        else:
            # stdout.write('\n')
            print('=====Upload thread checking:' + downloads_path)
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
                            global uploaded_count 
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


def yt_archiver(url, identifier, hide_date=False, hide_id=True, hide_format=True):
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
        'external_downloader': 'aria2c',
        'download_archive': downloads_path+ '.download-archive' , 
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
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

    #delete_none_completed_videos(ia_id)

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
                # No errors occured during download, Upload them...
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
