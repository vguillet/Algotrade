import datetime
import json
import sys
import time
import random
import os.path
from threading import *
from langdetect import detect  # to filter out anything which is not English

if sys.version_info[0] < 3:
    import got
else:
    import got3 as got
import \
    re  # hiermee urls uit tweets gehaald https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python

import got3 as got


def remove_urls(vTEXT):
    vTEXT = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', vTEXT, flags=re.MULTILINE)
    return (vTEXT)


# tyvm for internet and code sharing; with this the tweet can be cleaned


# import string # we dont want eg asian characters in our result; doesnt work
def clean(word):
    return ''.join(letter for letter in word.lower() if 'a' <= letter <= 'z')





def forbidden_words(file):
    forbidden_words_file = open(file, encoding='utf-8-sig')
    contents = forbidden_words_file.read()
    contents = contents.replace("\n", " ")
    list_of_words = contents.split(",")
    return list_of_words


def filter(file, tweet):
    forbidden_words_list = forbidden_words(file=file)
    for word in forbidden_words_list:
        if word in tweet:
            return True
    return False


def main(date):
    t = time.time()

    def printTweet(t):
        print(t.text)

    ## Example 1 - Get tweets by username
    # tweetCriteria = got.manager.TweetCriteria().setUsername('barackobama').setMaxTweets(1)
    # tweet = got.manager.TweetManager.getTweets(tweetCriteria)[0]

    # messing around myself
    dct = {}

    end_date = date + datetime.timedelta(days=1)

    tweetCriteria = got.manager.TweetCriteria().setTopTweets(True).setQuerySearch(searchterm).setSince(
        str(date)).setUntil(
        str(end_date)).setMaxTweets(tweets_per_day)
    # tweet = got.manager.TweetManager.getTweets(tweetCriteria)[5]
    # printTweet(tweet)
    tweet = got.manager.TweetManager.getTweets(tweetCriteria)
    lst = []
    for i in range(len(tweet)):
        tweetje = tweet[i].text
        tweetje = str(tweetje)
        tweetje = remove_urls(tweetje)
        tweetje = tweetje.lower()
        # tweetje = cleanString(tweetje)
        if len(tweetje) == 0:
            continue
        try:
            if detect(tweetje) != 'en':
                continue
        except:
            continue
        if filter(filterfile, tweetje):
            continue
        # tweetje = re.sub('[^A-Za-z0-9 ]+', '', tweetje) this filters out too much
        tweetje = [word for word in map(clean, tweetje.split()) if
                   word]  # there are some disadvantages; for example: cliché becomes cliche
        tweetje = ' '.join(tweetje)
        lst.append({"retweets": tweet[i].retweets, "favorites": tweet[i].favorites, "text": tweetje,
                    "link": tweet[i].permalink})

    dct.update({str(date): lst})

    with open("./tweets/" + str(searchterm) + "/" + str(date) + '.json', 'w') as outfile:
        json.dump(dct, outfile, indent=4)
    print("time taken to compute:", time.time() - t, "seconds")
    # tweetCriteria = got.manager.TweetCriteria().setQuerySearch(searchterm).setSince("2016-12-02").setUntil(
    #    "2016-12-03").setMaxTweets(maxtweets)
    # tweet = got.manager.TweetManager.getTweets(tweetCriteria)[5]
    # printTweet(tweet)
    # for i in range(maxtweets):
    #    tweetje = got.manager.TweetManager.getTweets(tweetCriteria)[i]
    #    tweetje = tweetje.text
    #    tweetje = str(tweetje)
    #    tweetje = remove_urls(tweetje)
    #    tweetje = tweetje.lower()
    #    # tweetje = cleanString(tweetje)
    #    if len(tweetje) == 0:
    #        continue
    #    # tweetje = re.sub('[^A-Za-z0-9 ]+', '', tweetje) this filters out too much
    #    tweetje = [word for word in map(clean, tweetje.split()) if
    #               word]  # there are some disadvantages; for example: cliché becomes cliche
    #    tweetje = ' '.join(tweetje)
    #    print(tweetje)


if __name__ == '__main__':

    tweets_per_day = 10000
    start_date = datetime.date(2017, 1, 1)
    days = 1
    filterfile = "forbiddenwords.txt"
    searchterm = 'iphone'
    day = datetime.date.today()
    while True:
        i = random.randint(0, 365*5)
        date = day - datetime.timedelta(days=i)
        filename = "./tweets/" + str(searchterm) + "/" + str(date) + '.json'
        if os.path.isfile(filename):
            with open(filename) as json_data:
                file = json.load(json_data)
            if len(file[str(date)]) < 10:
                print("Fetching for date {}, file was found empty".format(date))
                main(date)
            else:
                print("Date {} already fetched, moving on".format(date))
        else:
            print("Fetching for date {}".format(date))
            main(date)
