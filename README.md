# Reddify
Reddify is a Command Line Application that Creates and Updates a Spotify Playlist from Youtube URLs Submitted to a Music Subreddit.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install reddify.

```bash
pip install Reddify
```

## Getting Started
As per [Spotipy](https://spotipy.readthedocs.io/en/2.17.1/#getting-started)
"You will need to register your app at [My Dashboard](https://developer.spotify.com/dashboard/applications) to get the credentials necessary to make authorized calls (a client id and client secret)"

Once registered, make sure to set the following enviormental variables like so one at a time:
```bash
SETX SPOTIPY_CLIENT_ID 'your-spotify-client-id'
SETX SPOTIPY_CLIENT_SECRET 'your-spotify-client-secret'
SETX SPOTIPY_REDIRECT_URI 'your-app-redirect-url'
```

Double check your enviormental variables are set, make sure to restart CMD and enter "SET" to retrieve a list:
```bash
>>> SET

HOMEDRIVE=C:
SPOTIPY_CLIENT_ID='your-spotify-client-id'
SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
SPOTIPY_REDIRECT_URI='your-app-redirect-url'
.......
```

Note: If no enviormental variables are detected by "SET", that could mean the above "SETX" did not work for you. If so try the following:
```bash
SET SPOTIPY_CLIENT_ID='your-spotify-client-id'
SET SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
SET SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```

## Using the CLI
```bash
usage: reddify [-h] [-a] [-l]

Reddify CLI

positional arguments:
                 Subreddit Name

optional arguments:
  -h, --help     show this help message and exit
  -a , --after   Days after. Defaults to 1.
  -l , --limit   Max Number of Posts to Request. Defaults to all.

```

Example
```bash
>>> reddify metal -l 10

Queued > URI: spotify:track:4Jht9SukHPGW1widhLZPVC | Track: Exist - The Lottery
Queued > URI: spotify:track:6i5bMVwpQ3xZmLcLyYlE0G | Track: Sutrah - The Plunge
Queued > URI: spotify:track:3RUjDT1rPQyHOZTs5mjVEP | Track: Faceless Burial - Ravished To The Unknown

Updating > Playlist: #Reddify - Metal | # of Tracks in Update: 3
Complete > Runtime: 4.4979306
```

## Usage as a Module 
```python
from pyreddify import Reddify

Reddify('Metal', after=2)
```

## License
[MIT](https://choosealicense.com/licenses/mit/)