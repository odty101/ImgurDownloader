import logging
import os

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

from configuration import settings
from imgur_downloader import download_helper
from imgur_downloader.directory_helper import setup_download_dir

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
    def download_images(images, download_directory=None):
        """
        Return a list of tuples (URL, File) from a list of images

        :param images: A list of image objects to download
        :param download_directory: the parent directory to place the files in
        :return :
        """
        # Set the download directory
        if not download_directory:
            download_directory = settings.default_download_directory

        # Call the directory helper to setup the download directory
        download_dir = setup_download_dir(download_directory)

        download_list = []

        # Set the download dest and url for each image
        for image in images:
            # Set the download path for the image
            if not image.title or len(image.title) > 30:
                download_path = download_dir + '/' + image.id

            else:
                download_path = download_dir + '/' + image.title

                if os.path.exists(download_path):
                    download_path = download_path + '_' + str(image.id)

            if os.path.exists(download_path):
                logger.error('File {} already downloaded'.format(download_path))
                logger.error(FileExistsError)
            else:
                logging.debug('Adding {} to download_list'.format(image.link))
                download_list.append((image.link, download_path))

        download_helper.download_files(download_list)

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

    def download_album(self, album_id, album_title=None, parent_download_dir=None):
        """
        Download the imgur images from the specified album.

        :param album_id: The ID of the album to be downloaded
        :param album_title: The title of the album to prevent duplicate lookups or for custom names (used to name the
            download directory).
        :param parent_download_dir: The parent directory to use in addition to '~/ImgurDownloads'.
        """
        # Get album title if not passed
        if not album_title:
            try:
                album_title = self.client.get_album(album_id).title
            except ImgurClientError as e:
                logger.error('StatusCode: {}; Error: {}'.format(e.status_code, e.error_message))
                raise

        # Get the image objects for all images in album
        images = self.get_album_images(album_id)

        logger.info('Downloading {} images from album imgur.com/a/{}'.format(len(images), album_id))

        if not self.dry_run:
            # Create the Download directory for the album
            if not parent_download_dir:
                directory_name = str(album_id)
            else:
                directory_name = parent_download_dir + '/' + str(album_id)

            # Download the images to the specified directory
            self.download_images(images, directory_name)

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

        # Set the number of pages to one if not specified
        if not num_pages:
            num_pages = 1

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
            # Download all of the albums images
            for album in albums:
                logger.debug('Downloading album: {}'.format(album.link))
                self.download_album(album.id, album.title, sub_name)

            # Download all of the images to the download directory
            self.download_images(images, download_directory=sub_name)

            print('Subreddit {} Downloaded'.format(sub_name))
        else:
            print('DryRun!! - Would have downloaded images for {}'.format(sub_name))
