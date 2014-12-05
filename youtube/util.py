#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import division
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import gdata
import gdata.youtube
import gdata.youtube.service
import math
import codecs
from youtube.models import Comment
from youtube.models import Category
from youtube.models import Video
from django.utils import dateparse
from pygal.style import CleanStyle
import numpy as np
import pygal
from pytagcloud import defscale
from pygame import Color
from sklearn import linear_model
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from gdata.youtube.service import YouTubeService
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location='/media/photos')
import StringIO
import urllib
import base64


from nltk.tokenize import RegexpTokenizer

# define tokenizer
tokenizer = RegexpTokenizer(r'\w+')

filename_afinn = 'AFINN-111.txt'
afinn = dict(map(lambda (w, s): (w, int(s)),
                 [ws.strip().split('\t') for ws in codecs.open(filename_afinn, 'r', encoding='utf-8')]))


def save_video(video_id):
    """
    Given the unique youtube video id, the fields of the Video model are filled with the corresponding data
    and saved in the database. The score field is initialized with its default value 0. The rating gets a
    value 0 if it is not provided by the youtube client. If the Entry cannot be fetched an exception is raised.
    """
    
    yt_service = YouTubeService()

    try:
        video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)

    except gdata.service.RequestError, inst:
        raise

    category = Category.objects.get_or_create(id=video_details.media.category[0].text)

    rating = 0

    if video_details.rating:
        rating = (float(video_details.rating.average) - float(video_details.rating.min)) / \
                 (float(video_details.rating.max) - 1)

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
    """
    Returns the sentiment score(float) of the input string text using the afinn word list. Returns 0 when null string is input.
    """

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


def get_comments(video_id, index=1, max_entry=800):
    """
    Returns a list of the non duplicate, non null Comment objects from the Video with youtube id: video_id. It starts gathering Comments
    from the index comment and stops after at least max_entry Comments have been fetched.
    """
    yt_service = gdata.youtube.service.YouTubeService()

    comment_feed = "http://gdata.youtube.com/feeds/api/videos/{id}/comments?start-index={index}&max-results=50&orderby=published".format

    url = comment_feed(id=video_id, index=index)

    comments = []
    counter = 0

    while url and counter < max_entry:

        try:
            comment_feed = yt_service.GetYouTubeVideoCommentFeed(url)
        except gdata.service.RequestError, inst:
            comments = list()
            return comments

        comments.extend([comment for comment in comment_feed.entry if comment.content.text is not None])

        counter = len(comments)

        if comment_feed.GetNextLink() is not None:
            url = comment_feed.GetNextLink().href
        else:
            url = False

    return list(set(comments))


def savecomments(comments, video_id):
    """
    Saves the Comment objects (related to the Video with id video_id) comments into the database. Updates the
    score field of the specific Video if at least one Comment object has a sentiment.
    """
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
    """
    Outputs a list of tuples. The first element of each tuple is a word occuring both in the text field of the objects of
    the input list Comments and in the afinn word list. The second element is the number of occurences of the previous
    word in the text fields.
    """
    text = " ".join(comments.values_list('text', flat=True)).lower()
    words = tokenizer.tokenize(text)

    count = Counter(words)
    intersection = afinn.viewkeys() & count.viewkeys()
    frequency_list = [(word, count[word]) for word in intersection if count[word] > 1]

    return frequency_list


def get_total_data():

    """
    Outputs a dictionary with keys all the different id(s) of the object Category and values a list of tuples with
    elements the score and rating of each Video object, with the same category as its key.
    """
    cat_temp = [c.id for c in Category.objects.all()]
    cat_dict = {k: [] for k in cat_temp}

    for v in Video.objects.all():
        cat_dict[v.category.id].append((v.score, v.rating))

    return cat_dict


def category_chart(cat_dict):
    """
    Returns a XY object of the pygal module, based on the input dictionary cat_dict. The scatter plot produced has axes
    corresponding to the score of the Video (x-axis) and the rating (y-axis) and labels data according to their category.
    """
    cat_chart = pygal.XY(title=u'Sentiment vs Rating based on category', range=(0, 1),
                         style=CleanStyle, disable_xml_declaration=True, stroke=False,
                         x_title=u'Sentiment score', y_title=u'Youtube rating', title_font_size=20)
    for c in Category.objects.all():
        cat_chart.add(c.id, np.around(cat_dict[c.id], decimals=2))

    return cat_chart


def linear_regression(cat_dict):
    """
    Saves a figure in the images folder of the static path. The figure is a linear regression generated by the values of
    the input dictionary. Every value is a list of tuples. The first elements of the tuples correspond to the x-axis (score of
    the Video object) and the second to the y-axis (rating).
    """
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

    imgdata = StringIO.StringIO()
    plt.savefig(imgdata, format='png')
    imgdata.seek(0)

    return urllib.quote(base64.b64encode(imgdata.buf))


def video_charts(video_obj, comments):
    """
    Returns a list of two pygal charts, a Bar and a Pie, corresponding to a Video object and a list of Comment objects.
    The Bar is a histogram and the Pie indicates the percentage of the comments that have positive score.
    """
    score = np.around(video_obj.score, decimals=2)
    score_list = comments.values_list('afinn_score', flat=True)
    afinn_score_list = np.array(score_list)

    chart_data = np.histogram(afinn_score_list, range=(-5.5, 5.5), bins=11, density=True)[0] * 100
    chart_data = np.around(chart_data, decimals=2)
    charts = []

    bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle,
                          disable_xml_declaration=True, title_font_size=20)
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
    """
    Returns the Entry object of the most popular video feeds.
    """
    yt_service = gdata.youtube.service.YouTubeService()
    uri = "http://gdata.youtube.com/feeds/api/standardfeeds/most_popular?time=today"
    feed = yt_service.GetYouTubeVideoFeed(uri)
    return feed.entry


def searchresult(search_terms, sort='relevance', page=1):
    """
    Returns the Feed object after querying youtube search with input search_terms. The output contains the feed from the pages up
    until page (default=1).
    """
    yt_service = gdata.youtube.service.YouTubeService()

    query = gdata.youtube.service.YouTubeVideoQuery()
    query.vq = search_terms
    query.orderby = sort
    query.racy = 'include'
    query.max_results = 24
    query.start_index = 1 + (24 * (page - 1))

    result = yt_service.YouTubeQuery(query)
    feed = result.entry

    return feed


def tag_them(wordcounts, minsize=3, maxsize=36):
    """
    Mostly identical to the function make_tags from the module pytagcloud. Outputs a list of dictionaries, with 'tag' the first elements
    (words) from the wordcounts list of tuples, color green if those elements have positive value in the afinn dictionary, red if they
    have negative, and size dependent on the second elements(number of occurences) of the tuple.
    """
    counts = [tag[1] for tag in wordcounts]
    dictionary = afinn
    if not len(counts):
        return []

    maxcount = max(counts)
    mincount = min(counts)
    tags = []
    for word_count in wordcounts:
        color = Color(0, 255, 0) if (dictionary[word_count[0]] > 0) else Color(255, 0, 0)
        tags.append({'color': color, 'size': defscale(word_count[1], mincount, maxcount, minsize, maxsize),
                     'tag': word_count[0]})
    return tags
