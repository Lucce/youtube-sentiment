#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import division
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import gdata
import gdata.youtube
import gdata.youtube.service
import re
import math
import codecs
from youtube.models import Comment
from youtube.models import Category
from youtube.models import Video
from django.utils import dateparse
from pygal.style import CleanStyle
import numpy as np
import pygal

from collections import Counter

from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

my_data = json.loads(open("labmt.json").read())
happy_dict = {x['word']: float(x['happs']) for x in my_data['objects']}
new_happy_dict = {key: value for key, value in happy_dict.items() if not 4 <= value <= 6}


pattern_split = re.compile(r"\W+")

def get_wordlist():
    filenameAFINN = 'AFINN-111.txt'
    afinn = dict(map(lambda (w, s): (w, int(s)), [ws.strip().split('\t') for ws in codecs.open(filenameAFINN, 'r', encoding='utf-8')]))

    return afinn

def connect_youtube():

    try:
        return gdata.youtube.service.YouTubeService()
    except gdata.service.RequestError, inst:
        error = inst[0]

def save_video(video_id):

    yt_service = connect_youtube()

    try:
        video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)
    except gdata.service.RequestError, inst:
        raise
        # error = inst[0]
        # context = {'message': video_id, 'error': error}

    category = Category.objects.get_or_create(id=video_details.media.category[0].text)

    rating = 0

    if video_details.rating:
        rating = (float(video_details.rating.average) - float(video_details.rating.min)) / (float(video_details.rating.max)-1)
        print "video percent rating: {}".format(rating)

    video, new = Video.objects.get_or_create(id=video_id,
                                             category=category[0],
                                             title=video_details.media.title.text,
                                             rating=rating,
                                             date=dateparse.parse_datetime(video_details.published.text),
                                             image=video_details.media.thumbnail[0].url,
                                             view_count=video_details.statistics.view_count,
                                             )

    return video


def afinn_sentiment(text):


    afinn = get_wordlist()

    text = text.decode('utf-8')
    text = text.replace('\ufeff', "")
    text = text.strip().lower()

    words = tokenizer.tokenize(text)

    sentiments = map(lambda word: afinn.get(word, 0), words)

    if sentiments:
        sentiment = float(sum(sentiments))/math.sqrt(len(sentiments))
    else:
        sentiment = 0

    return sentiment


def labmt_sentiment(input):
    input = input.decode('utf-8')
    tokentext = tokenizer.tokenize(input)

    sentiment_words = Counter(dict.fromkeys(new_happy_dict.keys(), float('inf'))) & Counter(tokentext)
    sum_value = sum(sentiment_words.values())
    return sum([(happy_dict[word] * (freq / sum_value)) for word, freq in sentiment_words.iteritems()])

def get_comments(video_id, index=1, max_entry=800):

    yt_service = gdata.youtube.service.YouTubeService()

    comment_feed = "http://gdata.youtube.com/feeds/api/videos/{id}/comments?start-index={index}&max-results=50&orderby=published".format

    url = comment_feed(id=video_id,index=index)

    #comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)

    comments = []
    counter = 0

    while url and counter < max_entry:
        comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)

        comments.extend([comment for comment in comment_feed.entry if comment.content.text is not None])

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
    positive_count = 0
    negative_count = 0
    nonid = []
    id = set()

    temp_video = Video.objects.get(id=video_id)

    for comment in comments:
        # nonid.append(comment.id.text)
        # id.add(comment.id.text)
        #
        # print len(nonid)
        # print len(id)
        afinn_score = afinn_sentiment(comment.content.text)
        data.append(Comment(id=comment.id.text,
                            author=comment.author[0].name.text,
                            date=dateparse.parse_datetime(comment.published.text),
                            video=temp_video,
                            text=comment.content.text,
                            afinn_score=afinn_score))
        if afinn_score > 0:
            positive_count += 1
        if afinn_score < 0:
            negative_count += 1

    if (negative_count + positive_count) > 0:
        temp_video.score = float(positive_count) / (positive_count + negative_count)
        temp_video.save()

    data = set(data)
    Comment.objects.bulk_create(data)

def video_charts(video_obj, comments):
    print video_obj.score
    score = np.around(video_obj.score, decimals=2)
    score_list = comments.values_list('afinn_score',flat=True)
    afinn_score_list = np.array(score_list)

    chart_data = np.histogram(afinn_score_list, range=(-5.5, 5.5), bins=11, density=True)[0] * 100
    chart_data = np.around(chart_data, decimals=2)
    charts = []

    bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True)
    bar_chart.x_labels = map(str, range(-5, 6))
    bar_chart.y_labels = map(str, range(0, 110, 10))
    bar_chart.add('Comment Sentiment', chart_data)
    charts.append(bar_chart)

    pie_chart = pygal.Pie(style=CleanStyle, disable_xml_declaration=True)
    pie_chart.title = 'Browser usage in February 2012 (in %)'
    pie_chart.add('Positive', score)

    print score
    print 1 - score

    pie_chart.add('Negative', 1-score)
    charts.append(pie_chart)

    return charts

def getMostPopularVideos():

    yt_service = gdata.youtube.service.YouTubeService()
    uri = "http://gdata.youtube.com/feeds/api/standardfeeds/most_popular?time=today"
    feed = yt_service.GetYouTubeVideoFeed(uri)
    return feed.entry


def searchresult(search_terms,page=1):

    yt_service = gdata.youtube.service.YouTubeService()

    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.orderby = 'relevance'
    query.racy = 'include'
    query.max_results = 50

    result = yt_service.YouTubeQuery(query)
    feed = result.entry

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