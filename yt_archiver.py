import yt_downloader
import archive_uploader
import argparse


parser = argparse.ArgumentParser(description='Backup Youtube Channels to archive.org')
parser.add_argument('-u','--url', help='Url of Youtube channel or playlist.', required=True)
parser.add_argument('-i','--identifier', help='Identifier for archive.org page.', required=True)
args = vars(parser.parse_args())
yt_url = args['url']
ia_id = args['identifier']

if archive_uploader.create_identifier(ia_id):
    yt_downloader.yt_archiver(yt_url, ia_id)
else:
    print('Identifier Not available please choose another one.')