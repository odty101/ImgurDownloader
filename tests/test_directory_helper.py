import pytest
import os

from unittest.mock import MagicMock,patch
from imgur_downloader import directory_helper
from configuration import settings


def test_get_abs_path(monkeypatch):
    # Patch the call to os.path.isabs
    monkeypatch.setattr('os.path.isabs', MagicMock())

    path_name = directory_helper.get_abs_path('/Testing')

    assert path_name == '/Testing'


def test_get_abs_path_non_abs(monkeypatch):
    # Patch the calls to os.path
    monkeypatch.setattr(os.path, 'isabs', MagicMock(return_value=False))
    monkeypatch.setattr(os.path, 'expanduser', MagicMock(return_value='/home/pytest'))

    # Patch the call to settings
    monkeypatch.setattr(settings, 'default_download_directory', 'ImgurDownloader')

    path_name = directory_helper.get_abs_path('Testing')

    assert path_name == '/home/pytest/ImgurDownloader/Testing'

def test_setup_download_dir_file_exists(monkeypatch):
    # Patch the call to get_abs_path
    monkeypatch.setattr(directory_helper, 'get_abs_path', MagicMock(return_value='/test'))

    # Patch the calls to os.path
    monkeypatch.setattr(os.path, 'isfile', MagicMock())

    with pytest.raises(FileExistsError):
        directory_helper.setup_download_dir('testing')


def test_setup_download_dir_directory_exists(monkeypatch):
    # Patch the call to get_abs_path
    monkeypatch.setattr(directory_helper, 'get_abs_path', MagicMock(return_value='/test'))

    # Patch the calls to os.path
    monkeypatch.setattr(os.path, 'isfile', MagicMock(return_value=False))
    monkeypatch.setattr(os.path, 'isdir', MagicMock())

    path_name = directory_helper.setup_download_dir('Testing')

    assert path_name == '/test'

def test_setup_download_dir(monkeypatch):
    # Patch the call to get_abs_path
    monkeypatch.setattr(directory_helper, 'get_abs_path', MagicMock(return_value='/test'))

    # Patch the calls to os.path
    monkeypatch.setattr(os.path, 'isfile', MagicMock(return_value=False))
    monkeypatch.setattr(os.path, 'isdir', MagicMock(return_value=False))

    with patch('os.makedirs') as mock_makedir:
        directory_helper.setup_download_dir('Testing')
        mock_makedir.assert_called_once_with('/test')