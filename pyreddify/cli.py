import argparse
from pyreddify import Reddify

def main():
    parser = argparse.ArgumentParser(description='Reddify CLI')
        
    parser.add_argument(
        '-s', '--subreddit', type=str, metavar='', required=True, help='Subreddit Name')

    parser.add_argument(
        '-a', '--after', type=int, metavar='', help='Days Back', default=1)

    parser.add_argument(
        '-l', '--limit', type=int, metavar='', help='Max Number of Posts to Request', default=None)

    args = parser.parse_args()

    Reddify(args.subreddit, after=args.after, limit=args.limit)

if __name__ == '__main__':
    main()