import threading
import queue
import logging
import time

from requests import get

from configuration import settings


logger = logging.getLogger(__name__)
queue_lock = threading.Lock()


class DownloadWorker(threading.Thread):
    def __init__(self, work_queue, thread_id):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.thread_id = thread_id

    def run(self):
        worker(self.work_queue, self.thread_id)


def worker(work_queue, thread_id):
    logger.info('Thread {} is starting work'.format(thread_id))
    while True:
        queue_lock.acquire()
        logger.debug('Thread {}: Acquired queue_lock'.format(thread_id))
        if not work_queue.empty():
            logger.debug('Thread {}: work_queue not empty'.format(thread_id))
            item = work_queue.get()
            logger.debug('Thread {}: got work item {}'.format(thread_id, item))
            if item is None:
                queue_lock.release()
                logger.debug('Thread {}: Work item is None exiting'.format(thread_id))
                break
            link_url, download_path = item
            queue_lock.release()
            logger.info('Thread {}: Downloading {} to {}'.format(thread_id, link_url, download_path))
            download(link_url, download_path)
        else:
            queue_lock.release()
        time.sleep(1)


def download(url, file_path):
    """
    :param url: (str) The URL to be downloaded
    :param file_path: (str) The path of the file to be downloaded to
    :return:
    """
    # Open the file as a write buffer
    with open(file_path, 'wb') as out_file:
        # GET the file with request
        response = get(url)

        # Write the file to the buffer
        out_file.write(response.content)

    logger.info("Downloaded image from URL {} to path {}".format(url, file_path))


def download_files(files_to_download):
    """
    Download a file from the specified URL to the specified path

    :param files_to_download: A list of tuples specifying the download URL and dest file
    """
    # Retrieve the number of threads from settings
    num_of_threads = settings.num_of_threads

    # Create a queue to communicate with the workers and a lock
    work_queue = queue.Queue()
    threads = []

    # Create the worker threads
    for x in range(num_of_threads):
        thread = DownloadWorker(work_queue, x)
        thread.start()
        threads.append(thread)

    # Fill the queue with work
    queue_lock.acquire()
    for item in files_to_download:
        work_queue.put(item)
    queue_lock.release()

    # Wait for the work queue to empty
    while not work_queue.empty():
        pass

    # Wait for all of the thread to complete their work
    for x in range(num_of_threads):
        work_queue.put(None)
    for thread in threads:
        thread.join()

    print('Download Complete')
