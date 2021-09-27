from datetime import datetime
from apps.google_play import GooglePlayReviews


if __name__ == '__main__':
    kyivdigital = GooglePlayReviews(
        'com.kyivdigital',
        languages=['en', 'uk', 'ru', 'tt'],
        after=datetime(2021, 9, 25)
    )
    print(kyivdigital)
    # print(repr(kyivdigital))
    # print(kyivdigital.json())
    # kyivdigital.save_json(indent=2)

    # a1551 = apple_store_reviews('1551')
    # pprint(a1551.get_newest(datetime(2021, 7, 2)))
    # evernote = apple_store_reviews('evernote-notes-organizer')
    # pprint(evernote.get_newest(datetime(2021, 8, 9)))
