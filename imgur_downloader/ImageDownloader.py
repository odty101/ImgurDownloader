import logging

from urllib.request import urlopen


logger = logging.getLogger(__name__)


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
    # Set the Image number to 1 so each image will have a uniq image number
    image_num = 1

    for link in image_urls:
        # Set the download path for the image
        download_path = download_dir + '/image_{:03}'.format(image_num)

        download_image(link, download_path)

        # Increment the image number
        image_num += 1


