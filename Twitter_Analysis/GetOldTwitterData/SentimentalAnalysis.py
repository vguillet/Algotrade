import json
from textblob import TextBlob
import matplotlib.pyplot as plt
from datetime import timedelta, date, datetime
from scipy.signal import savgol_filter, medfilt


# Functions to read from json file
def read(file):
    # print(file)
    s = {}
    with open(file + '.json') as json_data:
        return json.load(json_data)


def get_text(tweet_data):
    return tweet_data['text']


def get_favorite(tweet_data):
    return tweet_data['favorites']


def get_retweets(tweet_data):
    return tweet_data['retweets']


# sentimental analysis
def get_sentiment(tweet_text):
    polarity_of_tweet = TextBlob(tweet_text).sentiment.polarity
    return polarity_of_tweet


def categorise_sentiment(sentiment_list, polarity, boundary=0):
    if polarity > boundary:
        sentiment_list[2] += 1
    elif polarity < -boundary:
        sentiment_list[0] += 1
    else:
        sentiment_list[1] += 1
    sentiment_list[4] += 1
    sentiment_list[3] += polarity
    return sentiment_list


def percentage(sentiment_list):
    percentage_list = []
    for i in range(3):
        percentage_list.append(sentiment_list[i] / sentiment_list[-1])
    return percentage_list


def plot(percentage_list, date):
    colors = ['red', 'blue', 'yellowgreen']
    patches, texts = plt.pie(percentage_list, colors=colors, startangle=90)
    labels = ['Negative', 'Neutral', 'Positive']
    plt.legend(patches, labels, loc="best")
    plt.title('Sentimental analysis for Apple on Twitter on {0}'.format(date))
    plt.axis('equal')
    plt.show()


# Use this function to get a list of sentiment polarities from a given start_date to end_date
# Set toggle_plot to True in order to see a plot over time
# Keyword is set to 'apple' by default, possible alternatives atm are ['iphone', 'ipad']
def polarity_over_time(start_date, end_date, toggle_plot=False, keyword='apple'):
    date_list = []
    polarity_list = []
    plot_dates = []

    current_date = start_date

    while current_date != end_date:
        date_list.append(str(current_date))
        plot_dates.append(current_date)
        current_date = current_date + timedelta(days=1)

    for day in date_list:
        file_str = "Twitter_Analysis/GetOldTwitterData/tweets/{}/{}".format(keyword, day)
        list_of_tweet_data = read(file_str)[day]
        polarity = 0
        deleted = 0

        for tweet in list_of_tweet_data:
            tweet_polarity = get_sentiment(get_text(tweet))

            if filter(get_text(tweet)):
                # print(get_text(tweet))
                tweet_polarity = 0
                deleted += 1
            # if get_favorite(tweet) > 0:
            #     tweet_polarity *= get_favorite(tweet)
            # if get_retweets(tweet):
            #     tweet_polarity *= get_retweets(tweet)
            polarity += tweet_polarity

        polarity /= len(list_of_tweet_data) - deleted
        polarity_list.append(polarity)

    polarity_list = savgol_filter(polarity_list, 13, 3)
    file = open("plot_data.txt", 'w')
    file.write(str(polarity_list) + "\n" + str(date_list))

    if toggle_plot:
        # plot2(polarity_list, plot_dates)
        plot2(polarity_list, plot_dates)
    return polarity_list


def plot2(polarity_list, date_list):
    plt.plot(date_list, polarity_list)
    plt.xlabel('Date')
    plt.ylabel('Polarity')
    # plt.ylim(-1, 1)
    plt.grid(b=True, which='both', axis='both')
    plt.title('Sentiment of Apple tweets between {0} and {1}'.format(date_list[0], date_list[-1]))
    plt.gcf().autofmt_xdate()
    plt.show()


def forbidden_words(file):
    forbidden_words_file = open(file, encoding='utf-8-sig')
    contents = forbidden_words_file.read()
    contents = contents.replace("\n", " ")
    list_of_words = contents.split(",")
    return list_of_words


def filter(tweet):
    for word in forbidden_words("Twitter_Analysis/GetOldTwitterData/forbiddenwords.txt"):
        if word in tweet:
            return True
    return False


def main(date):
    list_of_tweet_data = read("tweets")[date]
    sentiment_list = [0, 0, 0, 0, 0]
    for tweet in list_of_tweet_data:
        text = get_text(tweet)
        tweet_polarity = get_sentiment(text)
        categorise_sentiment(sentiment_list, tweet_polarity)
    print(sentiment_list)
    plot(percentage(sentiment_list), date)


if __name__ == '__main__':
    print(polarity_over_time(date(2016, 12, 1), date.today(), toggle_plot=True, keyword='apple'))
