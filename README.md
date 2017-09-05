# yt-archiver

Auto download Youtube channel or playlist & upload it to Archive.org page.

yt-archiver uses separate thread for uploading videos as they are being downloaded, significantly decreasing time & disk space needed for backup.

**N.b:** Downloaded files are uploaded & deleted automatically to save disk space.

**Intended to run & tested on Ubuntu 16.04 desktop & server. If you don't have a VPS,** <a href='https://github.com/pythonoma/yt-archiver/blob/master/README.md#best-to-run-on-vps-fast-downup-speeds'>**please Check THIS**</a>


Update System:
--------------------------------------------------------------------------------
```
sudo apt-get -y update && sudo apt-get -y upgrade
```


Install:
---------------------------------------------------------------------------------
```
curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/yt-archiver-install.sh -o yt-archiver-install.sh
chmod a+rx yt-archiver-install.sh
sudo ./yt-archiver-install.sh
```

Configure archive.org account:
---------------------------------------------------------------------------------

If you don't have account, create one here: <a href="https://archive.org/account/login.createaccount.php" target="_blank">https://archive.org/account/login.createaccount.php</a>


```
ia configure
```


(Optional) 
---------------------------------------------------------------------------------

Recommended to run in ```tmux``` session, so it continues running on the server. 
```
tmux new -s SESSION_NAME
```
Now you can close your ssh connection & when you login back you can view the session by:
```
tmux attach -t SESSION_NAME
```


Run
---------------------------------------------------------------------------------

```
yt-archiver.py -u <Youtube_URL> -i <Archive_Page_Identifier>
```
file name: ```uploadDate-Title```

ex: ```20170503-My video title.mp4```


```
yt-archiver.py -u <Youtube_URL> -i <Archive_Page_Identifier> -hd
```
file name: ```Title```

ex: ```My video title.mp4```


Best to run on VPS (fast down/up speeds). 
----------------------------------------------------------------------------

**I recommend the ones below which charge you per hour usage**
you can create a VPS, Backup your youtube videos & destroy the VPS => only charged for the hours you used not the whole month (usually a few cents!).


<a href="https://m.do.co/c/224d827b0d9b"  target="_blank">**1. DigitalOcean**</a>

The servers I tested this script on & it works fine (on Ubuntu 16.04 with 5$ droplet).

Droplets (DigitalOcean VPS intances) start at 0.007$/hour (yes less than a cent/hour!):

Get Free 10$ credit when you signup from this link: https://m.do.co/c/224d827b0d9b

<a href="https://m.do.co/c/224d827b0d9b" target="_blank"><img src="http://i.imgur.com/LVu6P6n.png"></a>


<a href="https://www.vultr.com/?ref=7208825"  target="_blank">**2. Vultr** </a>
------------------------------------------------------------------------------------
Vultr has a 0.004$/hour plan, even less than DigitalOcean (although not always available):

https://www.vultr.com/?ref=7208825

<a href="https://www.vultr.com/?ref=7208825"  target="_blank"><img src="https://www.vultr.com/media/banner_1.png" width="728" height="90"></a>

