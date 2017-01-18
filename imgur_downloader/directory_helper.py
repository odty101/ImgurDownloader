import os
import logging

from configuration import settings

logger = logging.getLogger(__name__)


def get_abs_path(path_name):
    """
    A function to return the path name based on if the input is abs or not
    :param path_name: relative or absolute path of the directory
    :return: an absolute path to the director
    """
    if os.path.isabs(path_name):
        abs_path = path_name
    else:
        abs_path = os.path.expanduser('~') + '/' + settings.default_download_directory + '/' + path_name

    return abs_path


def setup_download_dir(directory_name):
    """
    A helper function to create the download directory if it down not exist or is a file
    :param directory_name: Name of the directory to create
    :return: The absolute pathname of the directory just created.
    """
    # Get the absolute path of the directory
    abs_path = get_abs_path(directory_name)

    # If desired path is already a file raise
    if os.path.isfile(abs_path):
        logger.error('File exist at path {}'.format(abs_path))
        raise FileExistsError

    # Do not attempt to create the directory if it exists
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)

    logger.info('Download directory is: {}'.format(abs_path))

    return abs_path
