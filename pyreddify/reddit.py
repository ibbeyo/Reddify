from psaw.PushshiftAPI import PushshiftAPI
from collections import namedtuple

import re


class Subreddit:
    def __init__(self) -> None:
        self.subreddit = None
        
    def get_subreddit_submissions(self, subreddit, after=1, limit=None):
        '''
        Get Subreddit Submissions that contain youtube links.
        '''
        self.subreddit = subreddit

        options = {
            'after': after, 'subreddit': subreddit
        }

        if limit:
            options['limit'] = limit

        for submission in PushshiftAPI().search_submissions(**options):
            if submission.domain.startswith('youtu'):
                yield submission


    @classmethod
    def format_subreddit_title(self, title: str):
        '''
        Parses Reddit title for artist name and track name.
        '''

        Title = namedtuple('Title', field_names=['artist', 'track'], defaults=[None, None])

        strings = re.split(r'-|—', title)
        if len(strings) >= 2:
            return Title(
                *[re.sub(r'[\(\[].*?[\)\]]|\"', '', string.title()).strip() for string in strings]
            )
        return Title
