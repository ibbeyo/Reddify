# Reddify
Reddify is a Command Line Application that Creates and Updates a Spotify Playlist from Youtube URLs Submitted to a Music Subreddit.

<!-- ## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install reddify.

```bash
pip install Reddify
``` -->

## Getting Started
As per [Spotipy](https://spotipy.readthedocs.io/en/2.17.1/#getting-started)
"You will need to register your app at [My Dashboard](https://developer.spotify.com/dashboard/applications) to get the credentials necessary to make authorized calls (a client id and client secret)"

Once registered, make sure to set the following enviormental variables like so one at a time:
```
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
```
SET SPOTIPY_CLIENT_ID='your-spotify-client-id'
SET SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
SET SPOTIPY_REDIRECT_URI='your-app-redirect-url'
```


## Using the CLI
CLI will by default load from enviormental variable unless --load-envfile is used.
```bash
usage: cli.py [-h] [-a] [-l] [-ef]    

Reddify CLI

positional arguments:
                        Subreddit Name

optional arguments:
  -h, --help            show this help message and exit
  -a , --after          Days after. Defaults to 1.
  -l , --limit          Max Number of Posts to Request. Defaults to all.
  -ef , --load-envfile
                        Load Spotify Auth/Creds From .env file.
```

###### Sample Usage:
```
>>> reddify powermetal -l 10

Queued > URI: spotify:track:28UMKxUrrjYqTnpPvtjMED | Track: Aldious - Sweet Temptation - Live ver.
Queued > URI: spotify:track:74rWh6RlUV4pCHBVapIshX | Track: Theocracy - Easter
Queued > URI: spotify:track:3aKimOh0tmxuO43PC70GII | Track: Grailknights - Cthulhu
Queued > URI: spotify:track:6MKcVvnFB1iUIdJmjAry6i | Track: Helloween - Juggernaut
Queued > URI: spotify:track:1ge8Ots6ASC1va7kx348LJ | Track: Blind Guardian - Sadly Sings Destiny - Remastered 2017
Finished > Runtime: 4.3693469 | # Tracks Added: 5
```

## Using the Module

###### Importing the module:

```python
from pyreddify import SpotifyPlaylist
```

###### Loading Spotify Credentials By Parameters:
```python
playlist = SpotifyPlaylist(
    client_id='your-spotify-client-id', 
    client_secret='your-spotify-client-secret', 
    redirect_uri='your-app-redirect-url')
```


###### Reddify will check for both enviormental file or variable:
```python
envfile = 'you-env-file'

playlist = SpotifyPlaylist()
playlist.load_from_env(filepath=envfile)
```

###### Sample Usage:
```python
from pyreddify import SpotifyPlaylist

playlist = SpotifyPlaylist()
playlist.load_from_env()

for submission in playlist.get_subreddit_submissions('metalcore', limit=15, after=2):
    song = playlist.get_track(submission.title)
    if song:
        playlist.queue(song.track.uri)

playlist.update()
```

## License
[MIT](https://choosealicense.com/licenses/mit/)