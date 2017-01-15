import logging

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
    logger.debug("Downloading image from URL {} to path {}".format(
        image_url, download_path))

    with urlopen(image_url) as image, open(download_path, 'wb') as f:
        f.write(image.read())


def download_images(image_urls, download_dir):
    """
    Download an image from the specified URL to the specified path

    :param image_urls: (list) List of URLs for the images to be downloaded from.
    :param download_dir: (str) Directory for the image to be written to.
    """
    # Create a queue to communicate with the workers
    queue = Queue()

    # Create 12 worker threads ( TODO: dynamically adjust threads based on current system. )
    for x in range(12):
        worker = DownloadWorker(queue)
        # Setting daemon to True will allow the main thread to exit even if the workers are blocking
        worker.daemon = True
        worker.start()

    # Set the Image number to 1 so each image will have a uniq image number
    image_num = 1

    for link in image_urls:
        # Set the download path for the image
        download_path = download_dir + '/image_{:03}'.format(image_num)

        logger.info('Adding {} to queue'.format(link))
        queue.put((link, download_path))

        # Increment the image number
        image_num += 1

    queue.join()
