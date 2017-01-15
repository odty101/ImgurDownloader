import sys
import os
import argparse
import logging

from time import time
from imgur_downloader import AlbumDownloader

logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('url',
                        type=str,
                        nargs=1,
                        help="The URL of the Album to download.")

    parsed_args = parser.parse_args(args or sys.argv[1:])

    return parsed_args


def setup_download_dir(album_id):
    # Check if Path for album exists if not create
    path_name = os.path.expanduser('~/ImgurDownloader/') + str(album_id)
    if not os.path.isdir(path_name):
        os.makedirs(path_name)

    logger.info('Download directory is: {}'.format(path_name))

    return path_name


def main():
    album = AlbumDownloader.ImgurAlbumDownloader(album_url=parse_args().url[0])

    # Setup the directory to download to.
    download_dir = setup_download_dir(album_id=album.album_id)

    # Start the clock
    time_start = time()

    # Download the album to the directory
    album.download_album(download_dir=download_dir)

    # Calculate the time taken and print
    print('Album Downloaded in {} seconds'.format(time() - time_start))

    logger.info('Album downloaded to: {}'.format(download_dir))


if __name__ == '__main__':
    main()
