# yt-archiver

VPS intial setup:
```
curl -L https://github.com/pythonoma/vps-utilities/raw/master/vps-init-setup.sh -o /usr/bin/vps-init-setup.sh
chmod a+rx /usr/bin/vps-init-setup.sh 
vps-init-setup.sh
```
===========================================
Install:
```
curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/yt_archiver.py -o /usr/bin/yt_archiver.py
curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/archive_uploader.py -o /usr/bin/archive_uploader.py
curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/yt_downloader.py -o /usr/bin/yt_downloader.py

chmod a+rx /usr/bin/yt-archiver.py

yt-archiver.py
```
