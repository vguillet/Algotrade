import json
from textblob import TextBlob


def read(file):
    s = {}
    with open(file + '.json') as json_data:
        return json.load(json_data)


def get_data_from_date(json_data, date):
    return read(json_data)[date]


def get_text(tweet_data):
    return tweet_data['text']


def get_retweets(tweet_data):
    return tweet_data['retweets']


def get_favorites(tweet_data):
    return tweet_data['favorites']


def sentiment(json_data, date):
    polarity = 0
    list_of_tweet_data = get_data_from_date(json_data, date)
    for tweet_data in list_of_tweet_data:
        text = get_text(tweet_data)
        retweets = get_retweets(tweet_data)
        favorites = get_favorites(tweet_data)
        current_polarity = TextBlob(text).sentiment.polarity * (1+retweets+favorites)
        polarity += current_polarity
    return polarity


print(sentiment('tweets', '2016-01-01'))
print(sentiment('tweets', '2016-01-02'))
print(sentiment('tweets', '2016-01-03'))
