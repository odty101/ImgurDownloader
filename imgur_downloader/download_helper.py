import logging
import os

from urllib.request import urlopen
from queue import Queue
from threading import Thread


logger = logging.getLogger(__name__)


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            # Get work from the queue and expand the tuple
            link_url, download_path = self.queue.get()
            download_image(link_url, download_path)
            self.queue.task_done()


def download_image(image_url, download_path):
    """
    :param image_url: (str) The URL of the image to be downloaded
    :param download_path: (str) The path of the image to be downloaded to
            (Note if the download path exists it will be overridden).
    :return:
    """
    logger.debug("Downloading image from URL {} to path {}".format(
        image_url, download_path))

    try:
        with urlopen(image_url) as image, open(download_path, 'wb') as f:
            f.write(image.read())
    except:
        logger.error('Error downloading {}'.format(image_url))
        raise


def download_images(images, download_dir):
    """
    Download an image from the specified URL to the specified path

    :param images: (list) List of image objects to download.
    :param download_dir: (str) Directory for the image to be written to.
    """
    # Create a queue to communicate with the workers
    queue = Queue()

    # Create 12 worker threads
    for x in range(12):
        worker = DownloadWorker(queue)
        # Setting daemon to True will allow the main thread to exit even if the workers are blocking
        worker.daemon = True
        worker.start()

    for image in images:
        # Set the download path for the image
        if not image.title:
            download_path = download_dir + '/' + image.id
        else:
            download_path = download_dir + '/' + image.title

        if os.path.exists(download_path):
            download_path = download_path + '_' + str(image.id)

        logger.info('Adding {} to queue'.format(image.link))
        queue.put((image.link, download_path))

    queue.join()
