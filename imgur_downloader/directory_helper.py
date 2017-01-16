import os
import logging

logger = logging.getLogger(__name__)


def setup_download_dir(directory_name):
    """
    A helper function to create the download directory if it down not exist or is a file
    :param directory_name: Name of the directory to create
    :return: The absolute pathname of the directory just created.
    """
    # Check if Path for album exists if not create
    if os.path.isabs(directory_name):
        path_name = str(directory_name)
    else:
        path_name = os.path.expanduser('~/ImgurDownloader/') + str(directory_name)

    # If desired path is already a file raise
    if os.path.isfile(path_name):
        logger.error('File exist at path {}'.format(path_name))
        raise FileExistsError

    # Do not attempt to create the directory if it exists
    if not os.path.isdir(path_name):
        os.makedirs(path_name)

    logger.info('Download directory is: {}'.format(path_name))

    return path_name
