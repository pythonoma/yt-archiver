# yt-archiver

Auto download Youtube channel or playlist & upload it to Archive.org page.

yt-archiver is smart & can handle channels with xxxGb of content; when disk space runs out, it uploads & deletes downloaded files to free disk space. Then continue downloading the channel & uploading etc...
N.b: Downloaded files are uploaded & deleted automatically to save disk space.


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

If you don't have account, create one here: https://archive.org/account/login.createaccount.php

```
ia configure
```


Run:
---------------------------------------------------------------------------------
```
yt-archiver.py -u <Youtube_URL> -i <Archive_Page_Identifier>
```

FAQ:
----------------------------------------------------------------------------

Q: My free disk space is 15 GB & My channel has 50 videos about 50GB in size. How does it work?

A: yt-archiver downloads first videos (ex: 1-15 ) till no disk space is left (~15GB), then uploads them to archive.org & deletes them to free disk space. 

Then yt-archiver downloads the next 15 GB & uploads them etc.. till whole channel or playlist is backed up to archive.org

Best to run on VPS (fast down/up speeds). 
--------------------------------------------------------------------------------

**I recommend the ones below which charge you per hour usage **
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

