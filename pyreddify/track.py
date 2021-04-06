import re
import spotipy
from typing import Optional
from spotipy import client
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyTrack(object):
    def __init__(self, client_id, client_secret) -> None:
        super().__init__()
        
        self.client_id      = client_id
        self.client_secret  = client_secret
        self.metadata       = None

        self._is_available  : bool = False
        self._id            : Optional[str] = None
        self._uri           : Optional[str] = None
        self._name          : Optional[str] = None
        self._artist        : Optional[str] = None
        self._artist_id     : Optional[str] = None
        self._artist_uri    : Optional[str] = None
        self._album         : Optional[str] = None
        self._album_id      : Optional[str] = None
        self._album_art     : Optional[str] = None
        self._album_uri     : Optional[str] = None
        self._album_released: Optional[str] = None


    def search(self, title):
        "Search Spotify for track by title using the format: 'ARTIST - SONGNAME'."
        if len(string := re.split(r'-|—', title)) < 2:
            self.metadata = None
        
        else:
            artist = scrub_title(string[0])
            name = scrub_title(string[1])

            sp = spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=self.client_id, client_secret=self.client_secret
                )
            )

            res = sp.search(q=f'artist: {artist} track: {name}', limit=1, type='track')
        
            self.metadata = res['tracks']['items'][0] if res['tracks']['items'] else None
        return self


    @property
    def id(self):
        if self.is_available:
            if self._id: return self._id
            self._id = self.metadata['id']
        return self._id


    @property
    def uri(self):
        if self.is_available:
            if self._uri: return self._uri
            self._uri = self.metadata['uri']
        return self._uri


    @property
    def name(self):
        if self.is_available:
            if self._name: return self._name
            self._name = self.metadata['name']
        return self._name


    @property
    def artist(self):
        if self.is_available:
            if self._artist: return self._artist
            self._artist = self.metadata['artists'][0]['name']
        return self._artist


    @property
    def artist_id(self):
        if self.is_available:
            if self._artist_id: return self._artist_id
            self._artist_id = self.metadata['artists'][0]['id']
        return self._artist_id


    @property
    def artist_uri(self):
        if self.is_available:
            if self._artist_uri: return self._artist_uri
            self._artist_uri = self.metadata['artists'][0]['uri']
        return self._artist_uri


    @property
    def album(self):
        if self.is_available:
            if self._album: return self._album
            self._album = self.metadata['album'][0]['name']
        return self._album


    @property
    def album_art(self):
        if self.is_available:
            if self._album_art: return self._album_art
            self._album_art = self.metadata['album'][0]['images'][0]['url']
        return self._album_art


    @property
    def album_id(self):
        if self.is_available:
            if self._album_id: return self._album_id
            self._album_id = self.metadata['album'][0]['id']
        return self._album_id


    @property
    def album_uri(self):
        if self.is_available:
            if self._album_uri: return self._album_uri
            self._album_uri = self.metadata['album'][0]['uri']
        return self._album_uri


    @property
    def album_release(self):
        if self.is_available:
            if self._album_release: return self._album_release
            self._album_release = self.metadata['album'][0]['release_date']
        return self._album_release


    @property
    def is_available(self):
        self._is_available = True if self.metadata else False
        return self._is_available


def scrub_title(string):
    return re.sub(r'[\(\[].*?[\)\]]|\"', '', string.title().strip())