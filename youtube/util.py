#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import nltk
import json
import gdata
import gdata.youtube
import gdata.youtube.service
import re
import math
from timeit import Timer
import codecs
from youtube.models import Comment
from youtube.models import Video
from django.utils import dateparse

from collections import Counter

from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

my_data = json.loads(open("labmt.json").read())
happy_dict = {x['word']: float(x['happs']) for x in my_data['objects']}
new_happy_dict = {key: value for key, value in happy_dict.items() if not 4 <= value <= 6}


filenameAFINN = 'AFINN-111.txt'
afinn = dict(map(lambda (w, s): (w, int(s)), [ws.strip().split('\t') for ws in codecs.open(filenameAFINN, 'r',encoding='utf-8')]))

pattern_split = re.compile(r"\W+")

def afinn_sentiment(text):

    print text

    text = text.decode('utf-8')
    text = text.replace('\ufeff',"")
    text = text.strip().lower()

    #print text
    print "nltk tokens"
    words = tokenizer.tokenize(text)
    print words

    sentiments = map(lambda word: afinn.get(word, 0), words)

    if sentiments:
        sentiment = float(sum(sentiments))/math.sqrt(len(sentiments))
    else:
        sentiment = 0

    print sentiment
    return sentiment



def labmt_sentiment(input):
    input = input.decode('utf-8')

    #print input
    #tokentext = nltk.word_tokenize(input.lower())

    tokentext = tokenizer.tokenize(input)

    sentiment_words = Counter(dict.fromkeys(new_happy_dict.keys(), float('inf'))) & Counter(tokentext)
    sum_value = sum(sentiment_words.values())

    return sum([(happy_dict[word] * (freq / sum_value)) for word, freq in sentiment_words.iteritems()])

def getComments(video_id, index=1, max_entry=800):

    yt_service = gdata.youtube.service.YouTubeService()

    comment_feed = "http://gdata.youtube.com/feeds/api/videos/{id}/comments?start-index={index}&max-results=50&orderby=published".format

    url = comment_feed(id=video_id,index=index)

    #comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)

    comments = []
    counter = 0

    while url and counter < max_entry:
        comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)

        comments.extend([comment for comment in comment_feed.entry if comment.content.text is not None])
        #text.append(senanalyze(comments.text.content))

        counter = len(comments)

        print counter

        if comment_feed.GetNextLink() is not None:
            url = comment_feed.GetNextLink().href
            print url
        else:
            url = False

    return list(set(comments))

def savecomments(comments, video_id):

    data = []

    nonid = []
    id = set()

    temp_video = Video.objects.get(id=video_id)

    for comment in comments:
        # nonid.append(comment.id.text)
        # id.add(comment.id.text)
        #
        # print len(nonid)
        # print len(id)
        data.append(Comment(id=comment.id.text,
                            author=comment.author[0].name.text,
                            date=dateparse.parse_datetime(comment.published.text),
                            video=temp_video,
                            text=comment.content.text,
                            afinn_score=afinn_sentiment(comment.content.text)))

        # defaults= {'author': comment.author[0].name.text,
        #            'date': dateparse.parse_datetime(comment.published.text),
        #            'video': temp_video,
        #            'text': comment.content.text,
        #            'afinn_score': afinn_sentiment(comment.content.text)}

        # Comment.objects.update_or_create(Comment(id=comment.id.text,
        #                                          author=comment.author[0].name.text,
        #                                          date=dateparse.parse_datetime(comment.published.text),
        #                                          video=temp_video,
        #                                          text=comment.content.text,
        #                                          afinn_score=afinn_sentiment(comment.content.text)))

        #Comment.objects.update_or_create(id=comment.id.text, defaults=defaults)

    data = set(data)
    Comment.objects.bulk_create(data)

def getMostPopularVideos():

    yt_service = gdata.youtube.service.YouTubeService()
    uri = "http://gdata.youtube.com/feeds/api/standardfeeds/most_popular?time=today"
    feed = yt_service.GetYouTubeVideoFeed(uri)
    return feed.entry

def searchresult(search_terms,page=1):

    yt_service = gdata.youtube.service.YouTubeService()

    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.orderby = 'viewCount'
    query.racy = 'include'
    query.max_results = 50

    test = str(query) + "&v=2"

    print test
    comments = []

    result = yt_service.YouTubeQuery(query)
    feed = result.entry


    # list = []
    #
    # for entry in feed:
    #     #Video.objects.create_video(entry)
    #     print entry.media.title.text
    #     print entry.id.text.split("/")[-1]
    #     #list.append(Video(video_id=entry.id , title=entry.media.title.text))
    #     #list.append(Video.objects.create_video(entry))


    return feed

if __name__ == "__main__":

    string = unicode("what the fuck is wrong with you people saying we should beat her/rape her/kill her a kid, you dont have to like what she's doing but thats so fucked up").lower()

    print "afinn result"
    print afinn_sentiment(string)

    #print "labmt result"
    #print labmt_sentiment(string)

    # string = "i do not like it"
    # print afinn_sentiment(string)
    # print labmt_sentiment(string)
    #
    # t = Timer('labmt_sentiment("Finn is only a tiny bit stupid and Idiot")','from __main__ import labmt_sentiment')
    # print "time result"
    # print t.timeit(number=200)
    #
    # t = Timer('afinn_sentiment("Finn is only a tiny bit stupid and Idiot")','from __main__ import afinn_sentiment')
    # print "time result"
    # print t.timeit(number=200)