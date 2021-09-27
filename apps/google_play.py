from datetime import datetime as dt
from google_play_scraper import reviews, Sort
import json
import logging
from os import makedirs, path
from pprint import pformat

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s (%(asctime)s): %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# noinspection SpellCheckingInspection
class GooglePlayReviews:
    """
    Fetch and save GooglePlay reviews of selected application
        Example: kyivdigital = google_play_reviews('com.kyivdigital')

    Class variables defaults:
        - chunk_length = 100
        - output_date_format = '%d-%b-%Y, %H:%M:%S'
        - languages = ['en']

    self.reviews -> list of
    {
        'at': datetime(year, month, day, hour, minute, seconds),
        'content': str(Some user's review),
        'language': str(language),
        'repliedAt': datetime(year, month, day, hour, minute, seconds) | None,
        'replyContent': str(Some author's reply) | None,
        'reviewCreatedVersion': str(version of app),
        'reviewId': str(unique key string),
        'score': int(Stars),
        'thumbsUpCount': int(Number of review's likes),
        'userImage': str(url to user avatar),
        'userName': str(User Name)
    }

    Methods:
        - get_newest(after=today)
        - json(**kwargs passed json.dumps)
        - save_json(savedir='results', **kwargs passed self.json())
    """

    def __init__(self,
                 google_app_name: str,
                 after: dt = None,
                 languages: list = None,
                 chunk_length: int = 100,
                 output_date_format: str = '%d-%b-%Y, %H:%M:%S',
                 ) -> None:
        """
        Initialize instance variables and
        starts GooglePlay reviews fetching process for google_app_name
        """
        self.app_name = google_app_name
        if not after:
            after = dt(dt.now().year, dt.now().month, dt.now().day)
        if not languages:
            languages = ['en']
        self.chunk_length = chunk_length
        self.languages = languages
        self.output_date_format = output_date_format
        self.reviews_list = []
        self.get_newest(after)

    def __repr__(self) -> str:
        return (
            f'Total {len(self.reviews_list)} reviews:\n'
            f'{pformat(self.reviews_list)}'
        )

    def __str__(self) -> str:
        def filter_keys(d: dict) -> dict:
            keys = {'at', 'content', 'language', 'userName'}
            res = {k: v for k, v in d.items() if k in keys}
            res['at'] = res['at'].strftime(self.output_date_format)
            res['content'] = res['content'][:65]
            return res

        return json.dumps(
            list(map(filter_keys, self.reviews_list)),
            ensure_ascii=False,
            indent=2,
            sort_keys=True)

    def get_newest(
       self,
       after: dt = dt(dt.now().year, dt.now().month, dt.now().day)
    ) -> None:
        """
        Fetch sorted by date reviews created after selected date
        for self.languages into self.reviews
        """

        def add_language(d: dict) -> dict:
            d['language'] = language.lower()
            return d

        def remove_duplicates(comments: list) -> list:
            res, seen = [], set()
            for comment in comments:
                review_id = comment['reviewId']
                if review_id not in seen:
                    seen.add(review_id)
                    res.append(comment)
            return res

        logging.info(f'Fetching reviews for {self.app_name}')
        for language in self.languages:
            filtered, result, token = [], [], None
            while len(filtered) == len(result):
                result, token = reviews(
                    self.app_name,
                    lang=language,
                    sort=Sort.NEWEST,
                    count=self.chunk_length,
                    continuation_token=token)
                if not result:
                    break
                filtered = list(filter(lambda r: r['at'] >= after, result))
                self.reviews_list += list(map(add_language, filtered))
            self.reviews_list = remove_duplicates(self.reviews_list)
            self.reviews_list.sort(
                key=lambda review: review['at'],
                reverse=True
            )

    def json(self, **kwargs) -> str:
        """
        Return json formatted self.reviews, **kwargs passed to json.dumps()
        """

        def format_to_json(d: dict) -> dict:
            d['at'] = d['at'].strftime(self.output_date_format)
            if d['repliedAt']:
                d['repliedAt'] = \
                    d['repliedAt'].strftime(self.output_date_format)
            return d

        return json.dumps(
            list(map(format_to_json, self.reviews_list)),
            ensure_ascii=False,
            **kwargs)

    def save_json(self, savedir: str = 'results', **kwargs) -> None:
        """
        Save json formatted self.reviews into savedir/self.app_name.json file,
        **kwargs passed to self.json()
        """
        if not path.isdir(savedir):
            try:
                makedirs(savedir)
            except OSError:
                logging.error(
                    f'Creation of the result directory {savedir} failed')
                exit(2)
        file_name = path.join(savedir, f'{self.app_name}.json')
        logging.info(f'Saving reviews to "{file_name}"')
        with open(file_name, 'w', encoding='utf8') as f:
            f.write(self.json(**kwargs))


if __name__ == '__main__':
    print(GooglePlayReviews.__doc__)
