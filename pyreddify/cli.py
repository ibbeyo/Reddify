import argparse, sys, os, timeit
from pyreddify import Reddify


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

    reddify = Reddify(args.subreddit, after=args.after, limit=args.limit)

    if args.load_envfile:
        assert os.path.exists(args.load_envfile)
        reddify.load_from_env_file(args.load_envfile)
    else:
        reddify.load_from_env_vars()

    total = 0
    for submission in reddify.get_subreddit_submissions():
        song = reddify.get_spotify_track(submission.title)
        
        if song:
            if reddify.playlist_update(song.track.uri):
                total += 1
                notify(f'Added > URI: {song.track.uri} | Track: {song.artist.name} - {song.track.name}\n')

    stop = timeit.default_timer()
    notify(f'Finished > Runtime: {stop-start} | # Tracks Added: {total}\n')


if __name__ == '__main__':
    main()