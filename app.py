import datetime as dt
import re, sys, yaml, json, shutil, os
from urllib import parse
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from psaw.PushshiftAPI import PushshiftAPI
from youtube_search import YoutubeSearch


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
        parsed = parse.urlsplit(track.url)

        if parsed.netloc.endswith('.be'): song_id = parsed.path[1:]
        elif parsed.netloc.endswith('.com'): song_id = dict(parse.parse_qs(parsed.query)).get('v')[0]

        yt = YoutubeSearch(search_terms=song_id, max_results=1).to_json()
        song = json.loads(yt)['videos']
        titles = [song[0]['title'] if song else None, track.title]

        for x in range(2):

            if not titles[x]: continue
            result = self._spotSearch(q=titles[x])
            if result: self.tracks_queued.append(result['data']['uri'])
        
        return
    

    def updatePlaylist(self):
        self.apiAuthFlow.user_playlist_add_tracks(self._username, playlist_id=self._redditfy_playlist_id, tracks=list(set(self.tracks_queued)))
        return


if __name__ == '__main__':
    if not os.path.exists('config.yaml'):
        shutil.copy2('client.yaml', 'config.yaml')

    reddit = PushshiftAPI()
    spotify = SpotifyAPI()
    spotify.createPlaylist()

    for submission in reddit.search_submissions(after='30d', subreddit='melodicdeathmetal', filter=['url', 'domain', 'title'], limit=10):
        if submission.domain.startswith('youtu'):
            spotify.queueTrack(submission)

    spotify.updatePlaylist()

