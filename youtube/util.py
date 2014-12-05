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
import simplejson
from pytagcloud import defscale
from pygame import Color
from sklearn import linear_model
from matplotlib import pyplot as plt
from django.conf import settings
from collections import Counter

from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')

my_data = json.loads(open("labmt.json").read())
happy_dict = {x['word']: float(x['happs']) for x in my_data['objects']}
new_happy_dict = {key: value for key, value in happy_dict.items() if not 4 <= value <= 6}


pattern_split = re.compile(r"\W+")


def get_wordlist():
    filename_afinn = 'AFINN-111.txt'
    afinn = dict(map(lambda (w, s): (w, int(s)),
                     [ws.strip().split('\t') for ws in codecs.open(filename_afinn, 'r', encoding='utf-8')]))

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
        rating = (float(video_details.rating.average) - float(video_details.rating.min)) / \
                 (float(video_details.rating.max) - 1)

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
        sentiment = float(sum(sentiments)) / math.sqrt(len(sentiments))
    else:
        sentiment = 0

    return sentiment


def labmt_sentiment(input):
    text = input.decode('utf-8')
    token_text = tokenizer.tokenize(text)

    sentiment_words = Counter(dict.fromkeys(new_happy_dict.keys(), float('inf'))) & Counter(token_text)
    sum_value = sum(sentiment_words.values())
    return sum([(happy_dict[word] * (freq / sum_value)) for word, freq in sentiment_words.iteritems()])

def get_comments(video_id, index=1, max_entry=800):

def get_comments(video_id, index=1, max_entry=800):
    yt_service = gdata.youtube.service.YouTubeService()

    comment_feed = "http://gdata.youtube.com/feeds/api/videos/{id}/comments?start-index={index}&max-results=50&orderby=published".format

    url = comment_feed(id=video_id, index=index)

    # comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)

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

    temp_video = Video.objects.get(id=video_id)

    for comment in comments:

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

def create_frequency_list(comments):

    afinn = get_wordlist()
    text = ''
    for comment in comments:
        text += comment.text

    text.strip().lower()
    words = tokenizer.tokenize(text)

    count = Counter(words)
    intersection = afinn.viewkeys() & count.viewkeys()
    frequency_list = [(word, count[word]) for word in intersection if count[word] > 1]

    return frequency_list


def get_total_data():

    cat_temp = [c.id for c in Category.objects.all()]
    cat_dict = {k: [] for k in cat_temp}
    for v in Video.objects.all():
        cat_dict[v.category.id].append((v.score, v.rating))

    return cat_dict


def category_chart(cat_dict):

    cat_chart = pygal.XY(title=u'Sentiment vs Rating based on category', range=(0,1),
                         style=CleanStyle, disable_xml_declaration=True, stroke=False,
                         x_title=u'Sentiment score', y_title=u'Youtube rating', title_font_size=20)
    for c in Category.objects.all():
        cat_chart.add(c.id, np.around(cat_dict[c.id], decimals=2))

    return cat_chart


def linear_regression(cat_dict):

    l = cat_dict.values()
    data = [item for sublist in l for item in sublist]
    scores = np.array(zip(*data)[0])
    scores_w_intercept = np.array([np.ones(len(scores)), scores]).T
    ratings = np.array(zip(*data)[1])

    regr = linear_model.LinearRegression(fit_intercept=False)
    regr.fit(scores_w_intercept, ratings)
    x = np.linspace(0, max(scores), 20)
    y = x * regr.coef_[1] + regr.coef_[0]

    plt.figure()
    plt.title(u'Linear regression on the data')
    plt.xlabel(u'Sentiment score')
    plt.ylabel(u'Youtube rating')
    plt.axis([0, 1, 0, 1])
    plt.scatter(scores, ratings, marker='x')
    plt.plot(x, y)
    plt.savefig(settings.STATIC_PATH_WINDOWS+'\images\lin_reg.png')


def video_charts(video_obj, comments):

    score = np.around(video_obj.score, decimals=2)
    score_list = comments.values_list('afinn_score',flat=True)
    afinn_score_list = np.array(score_list)

    chart_data = np.histogram(afinn_score_list, range=(-5.5, 5.5), bins=11, density=True)[0] * 100
    chart_data = np.around(chart_data, decimals=2)
    charts = []

    bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True, title_font_size=20)
    bar_chart.x_labels = map(str, range(-5, 6))
    bar_chart.y_labels = map(str, range(0, 110, 10))
    bar_chart.add(u'Comment Sentiment', chart_data)
    charts.append(bar_chart)

    pie_chart = pygal.Pie(style=CleanStyle, disable_xml_declaration=True, title_font_size=20)
    pie_chart.title = u'Positive vs negative sentiment score (in %)'
    pie_chart.add(u'Positive', score)
    pie_chart.add(u'Negative', 1 - score)
    charts.append(pie_chart)

    return charts


def get_most_popularvideos():
    yt_service = gdata.youtube.service.YouTubeService()
    uri = "http://gdata.youtube.com/feeds/api/standardfeeds/most_popular?time=today"
    feed = yt_service.GetYouTubeVideoFeed(uri)
    return feed.entry


def searchresult(search_terms, page=1):
    print page
    yt_service = gdata.youtube.service.YouTubeService()

    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.orderby = 'relevance'
    query.racy = 'include'
    query.max_results = 24
    query.start_index = 1 + (24 * (page - 1))

    result = yt_service.YouTubeQuery(query)
    feed = result.entry

    return feed


def tag_them(wordcounts, minsize=3, maxsize=36, average=0):
    counts = [tag[1] for tag in wordcounts]
    dictionary = get_wordlist()
    if not len(counts):
        return []

    maxcount = max(counts)
    mincount = min(counts)
    tags = []
    for word_count in wordcounts:
        color = Color(0, 255, 0) if (dictionary[word_count[0]] > average) else Color(255, 0, 0)
        tags.append({'color': color, 'size': defscale(word_count[1], mincount, maxcount, minsize, maxsize),
                     'tag': word_count[0]})
    return tags


if __name__ == "__main__":
    string = unicode(
        "what the fuck is wrong with you people saying we should beat her/rape her/kill her a kid, you dont have to like what she's doing but thats so fucked up").lower()

    print "afinn result"
    print afinn_sentiment(string)

    # print "labmt result"
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