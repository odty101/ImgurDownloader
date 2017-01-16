# ImgurDownloader
A simple python program for downloading Imgur photos

### Usage

You must register your client with the Imgur API, and provide the Client-ID and Secret
 in settings.py in order to use the ImgurDownloader
 
#### Download an album

    imgur-download "imgur.com/a/{album-id}"

To download an album simply provide the URL to the album and the downloader will proceed
 to download all images in the album to the download directory
 
 
#### Download images from a Subreddit

    imgur-download reddit.com/r/{subreddit} --pages {num_pages}

To download all the Imgur images from a subreddit simple enter the URL. By default this
 will only download the first gallery page (100 images & albums). To specify more then 100
 items add '--page {num_pages}'

#### Get additional help

    imgur-download --help

Please be aware that I will update the help text of the argument parser before updating the README.
