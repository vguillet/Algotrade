import sys
if sys.version_info[0] < 3:
    import got
else:
    import got3 as got
import re # hiermee urls uit tweets gehaald https://stackoverflow.com/questions/11331982/how-to-remove-any-url-within-a-string-in-python
def remove_urls (vTEXT):
    vTEXT = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', vTEXT, flags=re.MULTILINE)
    return(vTEXT)

# tyvm for internet and code sharing; with this the tweet can be cleaned
def cleanString(incomingString):
    newstring = incomingString
    newstring = newstring.replace("!","")
    newstring = newstring.replace("@","")
    newstring = newstring.replace("#","")
    newstring = newstring.replace("$","")
    newstring = newstring.replace("%","")
    newstring = newstring.replace("^","")
    newstring = newstring.replace("&","and")
    newstring = newstring.replace("*","")
    newstring = newstring.replace("(","")
    newstring = newstring.replace(")","")
    newstring = newstring.replace("+","")
    newstring = newstring.replace("=","")
    newstring = newstring.replace("?","")
    newstring = newstring.replace("\'","")
    newstring = newstring.replace("\"","")
    newstring = newstring.replace("{","")
    newstring = newstring.replace("}","")
    newstring = newstring.replace("[","")
    newstring = newstring.replace("]","")
    newstring = newstring.replace("<","")
    newstring = newstring.replace(">","")
    newstring = newstring.replace("~","")
    newstring = newstring.replace("`","")
    newstring = newstring.replace(":","")
    newstring = newstring.replace(";","")
    newstring = newstring.replace("|","")
    newstring = newstring.replace("\\","")
    newstring = newstring.replace("/","")
    newstring = newstring.replace("-"," ")
    return newstring

#import string # we dont want eg asian characters in our result; doesnt work
def clean(word):
	return ''.join(letter for letter in word.lower() if 'a' <= letter <= 'z')

# this stuff is for sentimental analysis and the date:
from textblob import TextBlob # you will have to install these modules yourself!! otherwise wont run
from matplotlib import pyplot
from datetime import date
from datetime import timedelta


# CHANGE STUFF OVER HERE FOR THE SEARCH
maxtweets = 5
searchterm = 'apple'
days = 20


# prepping dates
today = date.today()
date_list = []
for i in range(0,days):
    date_list.append(today-timedelta(days=i))


def main():
    polarity_list = []
    for i in range(0,days-1):
        date_start = str(date_list[-(i+1)])
        date_end = str(date_list[-(i+2)])
        tweetCriteria = got.manager.TweetCriteria().setQuerySearch(searchterm).setSince(date_start).setUntil(date_end).setMaxTweets(maxtweets)
        polarity = 0
        for i in range(maxtweets):
            tweetje = got.manager.TweetManager.getTweets(tweetCriteria)[i]
            tweetje = tweetje.text
            tweetje = str(tweetje)
            tweetje = remove_urls(tweetje) # removes urls from tweets
            tweetje = tweetje.lower() # A a
            #tweetje = cleanString(tweetje) # removes stuff like ' , . ? etc. not necessary due to following command
            if len(tweetje) == 0: # empty tweets have to be removed
                continue
            tweetje = [word for word in map(clean, tweetje.split()) if word] #there are some disadvantages; for example: cliché becomes clich; but asian characters are deleted
            tweetje = ' '.join(tweetje)
            analysis = TextBlob(tweetje)
            polarity += analysis.sentiment.polarity
        polarity_list.append(polarity)

    # let's refactor the polarity_list between 1 and -1:
    max_factor = max(max(polarity_list),-1*min(polarity_list))
    for i in range(0,len(polarity_list)):
        polarity_list[i] = polarity_list[i]/max_factor
    polarity_list = polarity_list[::-1]

    # time to plot
    pyplot.plot(date_list[:len(date_list)-1], polarity_list)
    pyplot.xlabel('Date YYYY-MM-DD'); pyplot.ylabel('Polarity')
    pyplot.ylim(-1,1); pyplot.grid(b=True,which='both',axis='both')
    pyplot.title('Sentimental Analysis for {0}'.format(searchterm))
    pyplot.show()


if __name__ == '__main__':
	main()
