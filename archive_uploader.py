#!/usr/bin/env python3
from internetarchive import get_item, upload

def create_identifier( identifier):
    print('============================')
    print('Checking if identifier available...')
    item = get_item(identifier)
    # print(dir(item))
    create_test_file()
    try:
        item.upload('__.test', delete=True)
        print('Identifier available.')
        return True
    except:
        return False
    
def create_test_file():
    with open('__.test','w') as f:
        f.write('Test File')


def ar_upload(identifier, files_folder, auto_delete=True, verbose=True):
    item = get_item(identifier)
    # print(dir(item))
    md = dict(mediatype='movies',)
    try:
        item.upload(files_folder+'/', metadata=md, delete=auto_delete, verbose=verbose, checksum=True)
    except:
        print('Error Uploading')

