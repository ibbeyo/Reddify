import re, os, sys, timeit
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from psaw.PushshiftAPI import PushshiftAPI
from typing import Optional
from dotenv import load_dotenv

def notify(string):
    sys.stdout.write(string)
    sys.stdout.flush()


class Reddify:

    def __init__(
        self, 
        subreddit, 
        after=1, 
        limit: Optional[int] = None
    ):
        super().__init__()

        load_dotenv()

        self.subreddit          = subreddit
        self.after              = f'{after}d'
        self.limit              = limit
        self.playlist_name      = f'#Reddify - {subreddit}'.title()

        self._client_id         = os.getenv('SPOTIPY_CLIENT_ID')
        self._client_secret     = os.getenv('SPOTIPY_CLIENT_SECRET')
        self._redirect_uri      = os.getenv('SPOTIPY_REDIRECT_URI')
        self._playlist_id       = None
        self._playlist_tracks   = None
        self._username          = None

        self.playlist_seek_updates()


    @property
    def username(self):
        if self._username:
            return self._username
        self._username = self.spotify_authflow.current_user()['id']
        return self._username


    @property
    def spotify_credflow(self):
        client_creds_manager = SpotifyClientCredentials(
            client_id=self._client_id, client_secret=self._client_secret
        )
        return spotipy.Spotify(client_credentials_manager=client_creds_manager)


    @property
    def spotify_authflow(self):
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri=self._redirect_uri,
            scope='playlist-modify-public,playlist-modify-private,playlist-read-collaborative',
            cache_path=os.path.join(os.path.dirname(__file__), '.cache')
        ))


    @property
    def playlist_id(self):
        ''' Checks if playlist already exist and returns id.
            If playlist does not exist, playlist will get created and returns id'''

        if self._playlist_id:
            return self._playlist_id

        #Check if playlist exists
        playlists = self.spotify_authflow.user_playlists(self.username)
        if playlists['items']:
            for playlist in playlists['items']:
                if playlist['name'] == self.playlist_name: 
                    self._playlist_id = playlist['id']
                    return self._playlist_id

        #Create Playlist
        playlist = self.spotify_authflow.user_playlist_create(
            self.username, name=self.playlist_name)

        self._playlist_id = playlist['id']
        notify(f'\nCreated > Playlist: {self.playlist_name} | Playlist ID: {self._playlist_id}\n\n')
        return self._playlist_id


    @property
    def playlist_tracks(self):
        if self._playlist_tracks:
            return self._playlist_tracks

        current_tracks = self.spotify_authflow.user_playlist_tracks(
                self.username, playlist_id=self.playlist_id)

        self._playlist_tracks = [song['track']['uri'] for song in current_tracks['items']]
        return self._playlist_tracks        


    def playlist_seek_updates(self):
        start = timeit.default_timer()
        options = {
            'after'     : self.after,
            'subreddit' : self.subreddit,
            'filter'    : ['url', 'domain', 'title']
        }
        if self.limit: options.update({'limit': self.limit})

        uri_futures = self.playlist_tracks.copy()

        for submission in PushshiftAPI().search_submissions(**options):
            if submission.domain.startswith('youtu'):
                    
                if len(string := re.split(r'-|—', submission.title)) < 2: continue

                artist = string[0].title().strip()    
                track = re.sub(r'[\(\[].*?[\)\]]|\"', '', string[1].title().strip())

                result = self.spotify_credflow.search(
                    q=f'artist: {artist} track: {track}', limit=1, type='track'
                )

                if (tracks := result['tracks']['items']):
                    if (uri := tracks[0]['uri']) not in uri_futures:
                        uri_futures.append(uri)
                        notify(f'Queued > URI: {uri} | Track: {artist} - {track}\n')
                        continue
        
        if payload := set(uri_futures).difference(set(self.playlist_tracks)):
            notify(
                f'\nUpdating > Playlist: {self.playlist_name} | # of Tracks in Update: {len(payload)}\n'
            )

            self.spotify_authflow.user_playlist_add_tracks(
                self.username, playlist_id=self.playlist_id, tracks=payload)

        stop = timeit.default_timer()

        notify(f'Complete > Runtime: {stop-start}\n')
