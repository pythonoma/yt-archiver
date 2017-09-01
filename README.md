# yt-archiver

Auto download Youtube channel or playlist & upload it to Archive.org page.

yt-archiver is smart & can handle channels with xxxGb of content; when disk space runs out, it uploads & deletes downloaded files to free disk space. Then continue downloading the channel & uploading etc...
N.b: Downloaded files are uploaded & deleted automatically to save disk space.


---------------------------------------------------------------------------------

For example: 

Q: My free disk space is 15 GB & My channel has 50 videos about 50GB in size. How does it work?

A: yt-archiver downloads first videos (ex: 1-15 ) till no disk space is left (~15GB), then uploads them to archive.org & deletes them to free disk space. Then yt-archiver downloads the next 15 GB & uploads them etc.. till whole channel or playlist is backed up to archive.org

---------------------------------------------------------------------------------

Install:
---------------------------------------------------------------------------------
```
curl -L https://raw.githubusercontent.com/pythonoma/yt-archiver/master/install.sh -o install.sh
chmod a+rx install.sh
./install.sh
```

Configure archive.org account:
---------------------------------------------------------------------------------

```ia configure```

-------------------------------------------------

Run:
---------------------------------------------------------------------------------
```
yt-archiver.py -u <Youtube_URL> -i <Archive_Page_Identifier>
```
