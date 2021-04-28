import argparse, sys, timeit
from pyreddify import SpotifyPlaylist


def notify(string):
    sys.stdout.write(string)
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser(description='Reddify CLI')
        
    parser.add_argument(
        'subreddit', type=str, metavar='', help='Subreddit Name')

    parser.add_argument(
        '-a', '--after', type=int, metavar='', default=1, help='Days after. Defaults to 1.')

    parser.add_argument(
        '-l', '--limit', type=int, metavar='', help='Max Number of Posts to Request. Defaults to all.', default=None)

    parser.add_argument(
        '-ef', '--load-envfile', type=str, metavar='', help='Load Spotify Auth/Creds From .env file.', default=None)

    args = parser.parse_args()

    start = timeit.default_timer()

    playlist = SpotifyPlaylist()
    playlist.load_from_env(filepath=args.load_envfile)
    

    for submission in playlist.get_subreddit_submissions(subreddit=args.subredddit, after=args.after, limit=args.limit):
        song = playlist.get_track(submission.title)
        if song:
            if playlist.queue(song.track.uri):
                notify(f'Queued > URI: {song.track.uri} | Track: {song.artist.name} - {song.track.name}\n')

    total = playlist.update()

    stop = timeit.default_timer()

    notify(f'Finished > Runtime: {stop-start} | # Tracks Added: {total}\n')


if __name__ == '__main__':
    main()