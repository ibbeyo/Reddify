#add sys.argv cmd arguments
#youtube api - option to create youtube playlist

import argparse
import re, yaml, json, shutil, os
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from psaw.PushshiftAPI import PushshiftAPI
from pytube import YouTube
import datetime


def getUserConfig():
    with open('config.yaml') as fs:
        user_config = yaml.load(fs)
    return user_config


def updateUserConfig(k, v):
    config = getUserConfig()
    with open('config.yaml', 'w') as fs:
        config[k] = v
        yaml.dump(config, fs)
    return


class SpotifyAPI(object):

    def __init__(self):
        super().__init__()
        self.tracks_queued = []
        self._user_config = getUserConfig()
        self._client_secret = self._user_config['client_secret']
        self._client_id = self._user_config['client_id']
        self._username = self._user_config['username']
        self._scope = self._user_config['scope']
        self._redirect_uri = self._user_config['redirect_uri']
        self._redditfy_playlist_id = self._user_config['redditfy_playlist_id']

        self._client_creds_manager = SpotifyClientCredentials(
            client_id=self._client_id, client_secret=self._client_secret
        )

        self.apiAuthFlow = spotipy.Spotify(auth=self._getAuthToken())
        self.apiCredFlow = spotipy.Spotify(client_credentials_manager=self._client_creds_manager)


    def _getAuthToken(self):
        token = util.prompt_for_user_token(
            username        =   self._username,
            scope           =   self._scope,
            client_id       =   self._client_id,
            client_secret   =   self._client_secret,
            redirect_uri    =   self._redirect_uri
        )
        return token


    def _spotSearch(self, q):

        media = re.split(r'-|—', q, maxsplit=1)
        
        if len(media) < 2: return False

        artist = media[0].title().strip()
        song = re.sub(r'[\(\[].*?[\)\]]|\"', '', media[1]).title().strip()

        response = self.apiCredFlow.search(q=f'artist: {artist} track: {song}', limit=1, type='track')

        if len(response['tracks']['items']) == 0: return False

        return response['tracks']['items'][0]['uri']


    def createPlaylist(self):
        playist = 'Redditfy'

        if not self._redditfy_playlist_id:
            response = self.apiAuthFlow.user_playlist_create(self._username, name=playist)
            updateUserConfig('redditfy_playlist_id', response['id'])
            self.__setattr__('_redditfy_playlist_id', response['id'])
        return


    def doesTrackExists(self, track_uri):
        tracks = self.apiAuthFlow.user_playlist_tracks(self._username, playlist_id=self._redditfy_playlist_id)
        for track in tracks['items']:
            if track['track']['uri'] == track_uri: return True
        return False


    def queueTrack(self, track):
        yt = YouTube(url=track.url)
        titles = [yt.title, track.title]

        for title in titles:
            uri = self._spotSearch(q=title)

            if uri and not self.doesTrackExists(uri):
                self.tracks_queued.append(uri)
        return
    

    def updatePlaylist(self):
        if self.tracks_queued:
            self.apiAuthFlow.user_playlist_add_tracks(self._username, playlist_id=self._redditfy_playlist_id, tracks=list(set(self.tracks_queued)))
        return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reddify CLI')
    
    parser.add_argument('-s', '--subreddit', type=str, metavar='', required=True, help='Subreddit Name')
    parser.add_argument('-d', '--days', type=int, metavar='', help='Days Back', default=1)
    parser.add_argument('-l', '--limit', type=int, metavar='', help='Max Number of Posts to Request', default=100)
    args = parser.parse_args()

    query_options = {
        'after'     : f'{args.days}d',
        'subreddit' : args.subreddit,
        'filter'    : ['url', 'domain', 'title']
    }

    if args.limit: query_options['limit'] = args.limit

    if not os.path.exists('config.yaml'):
        shutil.move('client.yaml', 'config.yaml')

    reddit = PushshiftAPI()
    spotify = SpotifyAPI()
    spotify.createPlaylist()

    for submission in reddit.search_submissions(**query_options):
        if submission.domain.startswith('youtu'):
            spotify.queueTrack(submission)

    spotify.updatePlaylist()

