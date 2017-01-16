import sys
import argparse
import logging

from imgur_downloader import ImgurDownloader

logger = logging.getLogger(__name__)


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('url',
                        type=str,
                        nargs=1,
                        help="The URL or Sub to download.")
    parser.add_argument('--pages',
                        dest='pages',
                        type=int,
                        default=None,
                        help='Number of gallery (includes subreddits) pages to download.')

    parsed_args = parser.parse_args(args or sys.argv[1:])

    return parsed_args


def main():
    client = ImgurDownloader.Downloader(dry_run=True)

    parsed_args = parse_args()

    pages = parsed_args.pages
    url = parsed_args.url[0]

    if '/a/' in url:
        client.download_album(url)
    else:
        client.download_subreddit(url, num_pages=pages)


if __name__ == '__main__':
    main()
