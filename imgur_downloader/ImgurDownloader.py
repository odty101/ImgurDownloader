import logging
import re

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

from configuration import settings
from imgur_downloader import download_helper
from imgur_downloader import directory_helper

# Create a log handler
logger = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, dry_run=False):

        self._client = None
        self.dry_run = dry_run

    @property
    def client(self):
        """
        Creates a Imgur client
        :return: an Imgur client with the access keys set
        """
        if not self._client:
            self._client = ImgurClient(client_id=settings.client_id, client_secret=settings.client_secret)

        return self._client

    @staticmethod
    def get_album_id(album_url):
        """
        Takes the album URL and converts it to a album id
        :return: An Imgur album id corresponding to the album url
        """
        album_id = re.match(r"^.*/a/(\w*)$", album_url).group(1)

        return album_id

    def get_album_images(self, album_id):
        """
        Retrieve the list of Imgur image objects for the specified album.
        :param album_id: The id of the album to retrieve the image objects for
        :return: A list of Imgur image objects.
        """
        try:
            logging.debug("Retrieving URLs for album {}: https://imgur.com/a/{}".format(album_id, album_id))
            images = self.client.get_album_images(album_id)
        except ImgurClientError as e:
            logger.error("Problem retrieving links for album {}".format(album_id))
            logger.error(e.error_message)
            logger.error(e.status_code)
            raise

        return images

    def get_sub_images(self, sub_name, page):
        """
        Retrieve the list of image objects for the specified subreddit and page.
        :param sub_name: The name of the subreddit to retrieve the image objects for.
        :param page: The page in the subreddit to retrieve the image objects for.
        :return: A list of imgur image objects.
        """
        try:
            logger.debug('Retrieving URLs for sub: {}'.format(sub_name))
            images = self.client.subreddit_gallery(sub_name, page=page)
        except ImgurClientError as e:
            logger.error('Problem retrieving links for sub {}'.format(sub_name))
            logger.error(e.error_message)
            logger.error(e.status_code)
            raise

        return images

    def download_album(self, album_url, album_title=None, parent_download_dir=None):
        """
        Download the imgur images from the specified album.

        :param album_url: The URL of the album to be downloaded
        :param album_title: The title of the album to prevent duplicate lookups or for custom names (used to name the
            download directory).
        :param parent_download_dir: The parent directory to use in addition to '~/ImgurDownloads'.
        """
        # Convert the album URL to an ID
        album_id = self.get_album_id(album_url)

        # Get album title if not passed
        if not album_title:
            try:
                album_title = self.client.get_album(album_id).title
            except ImgurClientError as e:
                logger.error('Problem retrieving album title for album {}'.format(album_url))
                logger.error(e.error_message)
                logger.error(e.status_code)
                raise

        # Get the image objects for all images in album
        images = self.get_album_images(album_id)

        print('Downloading {} images from album {}'.format(len(images), album_url))

        if not self.dry_run:
            # Create the Download directory for the album
            if not parent_download_dir:
                directory_name = str(album_title)
            else:
                directory_name = parent_download_dir + '/' + str(album_title)

            download_dir = directory_helper.setup_download_dir(directory_name)

            # Download the images to the album's Folder
            download_helper.download_images(images, download_dir)

            print('Album {} downloaded'.format(album_title))
        else:
            print('DryRun!! - Would have downloaded images for {}'.format(album_title))

    def download_subreddit(self, sub_name, num_pages=None):
        """
        Download the images and albums from a subreddit gallery default is the first pages sorted newest
        :param sub_name : The name of the subreddit gallery to download from
        :param num_pages : The number of pages to download newest first
        """
        # Create a list of albums and a list of images to download
        images = []
        albums = []

        # Get a list of images and albums in the range of pages
        for page_num in range(0, num_pages):
            # Get a list of images objects for sub
            sub_images = self.get_sub_images(sub_name, page_num)

            for image in sub_images:
                if image.is_album:
                    albums.append(image)
                else:
                    images.append(image)

        print('Downloading {} Images & {} Albums from "r/{}"'.format(len(images), len(albums), sub_name))
        if not self.dry_run:
            # Create the Download directory for the sub
            sub_dir = directory_helper.setup_download_dir(str(sub_name))

            # Download all of the albums images
            for album in albums:
                logger.debug('Downloading album: {}'.format(album.link))
                self.download_album(album.link, album.title, sub_dir)

            # Download all of the images to the download directory
            download_helper.download_images(images, sub_dir)

            print('Subreddit {} Downloaded'.format(sub_name))
        else:
            print('DryRun!! - Would have downloaded images for {}'.format(sub_name))
