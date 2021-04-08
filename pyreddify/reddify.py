import os, re
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from psaw.PushshiftAPI import PushshiftAPI
from typing import Optional, Tuple
from dotenv import load_dotenv, dotenv_values
from pyreddify.metadata import SpotifyTrackItem


class Reddify:

    def __init__(self, subreddit, after=1, limit: Optional[Tuple[int, str]]=None, client_id: Optional[str]=None,
        client_secret: Optional[str]=None, redirect_uri: Optional[str]=None, username: Optional[str]=None):
        super().__init__()

        self.subreddit          = subreddit
        self.after              = f'{after}d'
        self.limit              = limit
        self.playlist_name      = f'#Reddify - {subreddit}'.title()

        self._client_id         = client_id
        self._client_secret     = client_secret
        self._redirect_uri      = redirect_uri
        self._username          = username
        self._playlist_id       = None


    def load_from_env_file(self, filepath=None):
        'Load Spotify Creds from a Env File'

        config = dotenv_values(filepath)
        self._client_id     = config['SPOTIPY_CLIENT_ID']
        self._client_secret = config['SPOTIPY_CLIENT_SECRET']
        self._redirect_uri  = config['SPOTIPY_REDIRECT_URI']

        
    def load_from_env_vars(self):
        'Load Spotify Creds from Env Variables'

        load_dotenv()
        self._client_id     = os.getenv('SPOTIPY_CLIENT_ID')
        self._client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        self._redirect_uri  = os.getenv('SPOTIPY_REDIRECT_URI')


    @property
    def username(self) -> str:

        if self._username:
            return self._username
        self._username = self.__spotify_authflow.current_user()['id']
        return self._username


    @property
    def __spotify_authflow(self):

        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self._client_id,
            client_secret=self._client_secret,
            redirect_uri=self._redirect_uri,
            scope='playlist-modify-public,playlist-modify-private,playlist-read-collaborative',
            cache_path=os.path.join(os.path.dirname(__file__), '.cache')
        ))


    @property
    def __spotify_credflow(self):
        return spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self._client_id, client_secret=self._client_secret
            )
        )


    @property
    def playlist_id(self) -> Tuple[str, None]:
        ''' Checks if playlist already exist and returns id.
            If playlist does not exist, playlist will get created and returns id'''

        if self._playlist_id:
            return self._playlist_id

        #Check if playlist exists
        playlists = self.__spotify_authflow.user_playlists(self.username)
        if playlists['items']:
            for playlist in playlists['items']:
                if playlist['name'] == self.playlist_name: 
                    self._playlist_id = playlist['id']
                    return self._playlist_id

        #Create Playlist
        playlist = self.__spotify_authflow.user_playlist_create(
            self.username, name=self.playlist_name)

        self._playlist_id = playlist['id']
        return self._playlist_id


    def playlist_track_exist(self, track_uri: str) -> bool:
        'Checks if track exists within the playlist.'

        if track_uri:
            tracks = self.__spotify_authflow.user_playlist_tracks(
                    self.username, playlist_id=self.playlist_id)

            if track_uri in [song['track']['uri'] for song in tracks['items']]:
                return True
        return False


    def playlist_update(self, track_uri: str) -> bool:
        'Updates the playlist with the new track. Will check for dupes.'

        if not self.playlist_track_exist(track_uri):
            self.__spotify_authflow.user_playlist_add_tracks(
                self.username, playlist_id=self.playlist_id, tracks=[track_uri])
            return True
        return False


    def get_subreddit_submissions(self):
        'Get subreddit submissions.'

        options = {
            'after'     : self.after,
            'subreddit' : self.subreddit
        }
        if self.limit: options.update({'limit': self.limit})

        for submission in PushshiftAPI().search_submissions(**options):
            if submission.domain.startswith('youtu'):
                yield submission
    

    def get_spotify_track(self, title) -> SpotifyTrackItem:
        'Get a spotify track.'

        def format_title(string):
            return re.sub(r'[\(\[].*?[\)\]]|\"', '', string.title().strip())
            
        if len(string := re.split(r'-|—', title)) >= 2:
        
            artist = format_title(string[0])
            name = format_title(string[1])

            res = self.__spotify_credflow.search(
                q=f'artist: {artist} track: {name}', limit=1, type='track'
            )

            if metadata := res['tracks']['items']:
                return SpotifyTrackItem(metadata=metadata[0])

        return None