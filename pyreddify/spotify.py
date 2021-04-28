from typing import final
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from pyreddify.reddit import Subreddit
from dataclasses import dataclass
from dotenv import load_dotenv, dotenv_values

import os
import spotipy


@dataclass
class TrackItem:
    id  : str
    uri : str
    name: str


@dataclass
class ArtistItem(TrackItem):
    pass


@dataclass
class AlbumItem(TrackItem):
    art         : str
    release_date: str
    total_tracks: str


@dataclass
class PlaylistItem:
    artist  : ArtistItem
    album   : AlbumItem
    track   : TrackItem


class SpotifyPlaylist(Subreddit):

    def __init__(self,
        client_id=None, 
        client_secret=None, 
        redirect_uri=None, 
        playlist_name=None) -> None:

        super().__init__()

        self.client_id      = client_id
        self.client_secret  = client_secret
        self.redirect_uri   = redirect_uri
        self._playlist_name = playlist_name
        self._playlist_id   = None

        if not all([client_id, client_secret, redirect_uri]):
            self.load_from_env()
        
        self.username = self.__authflow.current_user()['id']

        self.queued_track_uris = set()


    def load_from_env(self, filepath=None):
        if filepath:
            env = dotenv_values(filepath)
            self.client_id       = env['SPOTIPY_CLIENT_ID']
            self.client_secret   = env['SPOTIPY_CLIENT_SECRET']
            self.redirect_uri    = env['SPOTIPY_REDIRECT_URI']
            return

        load_dotenv()
        self.client_id       = os.getenv('SPOTIPY_CLIENT_ID')
        self.client_secret   = os.getenv('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri    = os.getenv('SPOTIPY_REDIRECT_URI')
        return

    
    @property
    def __authflow(self):
        try:
            return spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope='playlist-modify-public,playlist-modify-private,playlist-read-collaborative',
                cache_path=os.path.join(os.path.dirname(__file__), '.cache')
            ))
        except Exception:
            raise


    @property
    def __credflow(self):
        try:
            return spotipy.Spotify(
                client_credentials_manager=SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            )
        except Exception:
            raise

    
    @property
    def id(self):
        if self._playlist_id:
            return self._playlist_id
        
        playlists = self.__authflow.user_playlists(self.username)
        for playlist in playlists['items']:
            if playlist['name'] == self.name:
                self._playlist_id = playlist['id']
                return self._playlist_id
        
        playlist = self.__authflow.user_playlist_create(self.username, name=self.name)
        self._playlist_id = playlist['id']
        return self._playlist_id

    
    @property
    def name(self):
        if self._playlist_name:
            return self._playlist_name
        
        elif self.subreddit:
            self._playlist_name = f'#Reddify - {self.subreddit}'.title()

        else:
            raise Exception('No playlist name was found.')


    def queue(self, track_uri: str):
        '''
        Add a track to the playlist queue.
        '''
        assert track_uri.startswith('spotify:track')
        self.queued_track_uris.add(track_uri)


    def update(self):
        '''
        Updates the playlist with new tracks in the playlist queue. Will check for duplicates.'
        '''
        tracks = self.__authflow.user_playlist_tracks(self.username, playlist_id=self.id)
        existing_track_uris = [song['track']['uri'] for song in tracks['items']]

        while len(existing_track_uris) < tracks['total']:
            tracks = self.__authflow.user_playlist_tracks(
                self.username, playlist_id=self.id, offset=len(existing_track_uris)
            )
            existing_track_uris.extend([song['track']['uri'] for song in tracks['items']])
        
        unique_tracks = self.queued_track_uris.difference(existing_track_uris)
        self.queued_track_uris.clear()

        if tracks:
            try:
                self.__authflow.user_playlist_add_tracks(
                    self.username, playlist_id=self.id, tracks=list(unique_tracks)
                )
                return len(unique_tracks)
            except spotipy.exceptions.SpotifyException:
                raise
        return 0


    def get_track(self, title) -> PlaylistItem:
        '''
        Get a spotify track.
        '''
        title = self.format_subreddit_title(title)
        if title:
            response = self.__credflow.search(
                q=f'artist: {title.artist} track: {title.track}', limit=1, type='track'
            )

            item = response['tracks']['items']
            if item:
                track = item[0]
                album = item[0]['album']
                artist = item[0]['artists'][0]

                return PlaylistItem(
                    track=TrackItem(
                        track['id'], 
                        track['uri'], 
                        track['name']
                    ),
                    artist=ArtistItem(
                        artist['id'], 
                        artist['uri'], 
                        artist['name']
                    ),
                    album=AlbumItem(
                        album['id'], 
                        album['uri'], 
                        album['name'], 
                        album['images'][0]['url'], 
                        album['release_date'], 
                        album['total_tracks']
                    )
                )

        return None