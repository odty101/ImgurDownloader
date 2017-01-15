import logging
import re

from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

from configuration import settings
from imgur_downloader import ImageDownloader

# Create a log handler
logger = logging.getLogger(__name__)


class ImgurAlbumDownloader(object):
    def __init__(self, album_url):
        self.album_url = album_url

        self._client = None
        self._album_id = None
        self._links = None

    @property
    def client(self):
        """
        Creates a imgur client
        :return:
            _client (ImgurClient): an imgur client with the access keys set
        """
        if not self._client:
            self._client = ImgurClient(client_id=settings.client_id, client_secret=settings.client_secret)

        return self._client

    @property
    def album_id(self):
        """
        Takes the album URL and converts it to a album id
        :return:
            _album_id (str): an imgur album id corresponding to the album url
        """
        if not self._album_id:
            self._album_id = re.match(r"^.*\/a\/(\w*)$", self.album_url).group(1)

        return self._album_id

    @property
    def album_links(self):
        """
        Get the URLs for the images in an imgur album

        :return:
            links (list): a list of the imgur URLs from the specified album
        """
        if not self._links:
            try:
                logging.debug("Retriving URLs for album {}: {}".format(self.album_id, self.album_url))
                items = self.client.get_album_images(album_id=self.album_id)
            except ImgurClientError as e:
                logger.error("Problem retrieving links for album {}".format(self.album_url))
                logger.error(e.error_message)
                logger.error(e.status_code)
                raise

            # Create a list of containing just the imgur image urls
            self._links = []

            for item in items:
                if item.link.endswith('.jpg'):
                    self._links.append(item.link)

        return self._links

    def download_album(self, download_dir):
        """
        Download the entire album to path

        :param download_dir: (str) The directory to download the album to
        :return None:
        """
        ImageDownloader.download_images(image_urls=self.album_links, download_dir=download_dir)
