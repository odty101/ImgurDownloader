import pytest
from unittest.mock import MagicMock, patch, mock_open, Mock

import queue
import threading

from imgur_downloader import download_helper
from configuration import settings


def test_download_worker():
    # Setup a work_queue to pass to the worker
    work_queue = queue.Queue()

    test_worker = download_helper.DownloadWorker(work_queue=work_queue, thread_id=1)

    assert test_worker.work_queue == work_queue
    assert test_worker.thread_id == 1


def test_download_worker_run():
    # Mock out the download worker object
    work_queue = queue.Queue()
    mock_download_worker = download_helper.DownloadWorker(work_queue=work_queue, thread_id=1)

    with patch('imgur_downloader.download_helper.worker') as mock_worker:
        mock_download_worker.run()
        mock_worker.assert_called_once()


@pytest.mark.parametrize('num_threads, amount_of_work', [(1, 2),
                                                         (2, 1)])
def test_worker(monkeypatch, num_threads, amount_of_work):
    # Mock the call to download
    monkeypatch.setattr('imgur_downloader.download_helper.download', MagicMock())

    # Setup the threading lock
    queue_lock = threading.Lock()
    work_queue = queue.Queue()

    # Create the threads
    threads = []

    for x in range(num_threads):
        thread = download_helper.DownloadWorker(work_queue=work_queue, thread_id=x)
        thread.start()
        threads.append(thread)

    # Add some work to the queue
    queue_lock.acquire()
    for x in range(amount_of_work):
        work_queue.put(('url: {}'.format(x), 'path: {}'.format(x)))
    queue_lock.release()

    # Let the work exit cleanly
    # Wait for the work queue to empty
    while not work_queue.empty():
        pass

    # Wait for all of the thread to complete their work
    for x in range(num_threads):
        work_queue.put(None)
    for thread in threads:
        thread.join()

    # Lets make some assertions
    assert work_queue.empty()

    for thread in threads:
        assert not thread.is_alive()


def test_download(monkeypatch):
    # mock the call to requests
    monkeypatch.setattr(download_helper, 'get', MagicMock())

    # Patch builtin open
    with patch('imgur_downloader.download_helper.open', mock_open(), create=True) as m_open:
        download_helper.download('URL', 'PATH')

        assert m_open.called
        assert download_helper.get.called