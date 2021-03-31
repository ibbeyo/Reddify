import re
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from psaw.PushshiftAPI import PushshiftAPI
from pytube import YouTube


class ReddifyAPI(object):
    scope = 'playlist-modify-public,playlist-modify-private,playlist-read-collaborative'


    def __init__(self, username, client_id, client_secret, redirect_uri):
        super().__init__()

        self.song_queue = set()
        self.ignore_artist = list()
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.set_spotify_auth_scopes()
        

    def set_spotify_auth_scopes(self):
        
        token = util.prompt_for_user_token(
            username        =   self.username,
            scope           =   self.scope,
            client_id       =   self.client_id,
            client_secret   =   self.client_secret,
            redirect_uri    =   self.redirect_uri
        )

        client_creds_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )

        self._spotAuthFlow = spotipy.Spotify(auth=token)

        self._spotCredFlow = spotipy.Spotify(client_credentials_manager=client_creds_manager)


    def does_song_exist(self, song_uri):

        songs = self._spotAuthFlow.user_playlist_tracks(
            self.username, playlist_id=self.playlist_id
        )

        for song in songs['items']:
            if song['track']['uri'] == song_uri:
                return True
        return False


    def playlist_create(self, playlist_name):
        ''' Checks if playlist already exist and returns id.
            If playlist does not exist, playlist will get created and returns id'''

        playlists = self._spotAuthFlow.user_playlists(self.username)
        if playlists['items']:
            for playlist in playlists['items']:
                if playlist['name'] == playlist_name: 
                    return playlist['id']

        playlist = self._spotAuthFlow.user_playlist_create(self.username, name=playlist_name)
        return playlist['id']
    

    def playlist_update(self):
        if self.song_queue:
            self._spotAuthFlow.user_playlist_add_tracks(
                self.username, playlist_id=self.playlist_id, tracks=list(self.song_queue)
            )


    def playlist_queue(self, song_url, song_title):
        possible_query = [song_title]
        try:
            yt = YouTube(url=song_url)
            possible_query.insert(0, yt.title)

        except Exception: pass
        

        for query in possible_query:

            title = re.split(r'-|—', query, maxsplit=1)
            
            if len(title) < 2: return False

            artist = title[0].title().strip()
            
            if artist in self.ignore_artist: break
            
            song = re.sub(r'[\(\[].*?[\)\]]|\"', '', title[1].title().strip())

            results = self._spotCredFlow.search(
                q=f'artist: {artist} track: {song}', limit=1, type='track'
            )

            if len(results['tracks']['items']) > 0:
                song_uri = results['tracks']['items'][0]['uri']

                if not self.does_song_exist(song_uri):
                    self.song_queue.add(song_uri)
                    break

        return


    def playlist_from_subreddit(self, subreddit, after=1, limit=None, ignore_artist=None):

        playlist_name = f'#Reddify - {subreddit}'.title()
        self.playlist_id = self.playlist_create(playlist_name)

        if isinstance(ignore_artist, list):
            self.ignore_artist = [artist.title() for artist in ignore_artist]

        search_options = {
            'after'     : f'{after}d',
            'subreddit' : subreddit,
            'filter'    : ['url', 'domain', 'title']
        }
        if limit: search_options.update({'limit': limit})

        for submission in PushshiftAPI().search_submissions(**search_options):
            if submission.domain.startswith('youtu'):
                self.playlist_queue(submission.url, submission.title)

        self.playlist_update()


def main():
    import argparse
    from dotenv import dotenv_values

    parser = argparse.ArgumentParser(description='Reddify CLI')
    
    parser.add_argument(
        '-s', '--subreddit', type=str, metavar='', required=True, help='Subreddit Name')

    parser.add_argument(
        '-d', '--days', type=int, metavar='', help='Days Back', default=1)

    parser.add_argument(
        '-l', '--limit', type=int, metavar='', help='Max Number of Posts to Request', default=None)

    parser.add_argument(
        '-i', '--ignore-artist', metavar='', help='Artist to Ignore', default=None, nargs='*')

    args = parser.parse_args()

    reddify = ReddifyAPI(**{**dotenv_values(".env")})
    
    reddify.playlist_from_subreddit(
        subreddit=args.subreddit, after=args.days, limit=args.limit, ignore_artist=args.ignore_artist)


if __name__ == '__main__':
    main()