from datetime import datetime
import json
import logging
from pprint import pformat
from typing import List

# https://pypi.org/project/app-store-scraper/
from app_store_scraper import AppStore


class apple_store_reviews():
    languages = (
        {'country': 'us'},
        {'country': 'ua'},
    )
    reviews = []

    def __init__(self, apple_app_name: str) -> None:
        self.app_name = apple_app_name

    def get_newest(self,
        after=datetime(
            datetime.now().year, datetime.now().month, datetime.now().day)
        ) -> List:
        for language in self.languages:
            apple_app = AppStore(
                country=language['country'],
                app_name=self.app_name
            )
            apple_app.review(
                how_many=1,
                #after=after
            )
            self.reviews += apple_app.reviews
        return self.reviews
