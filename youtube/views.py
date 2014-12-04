from __future__ import division
from django.shortcuts import render
from youtube import util
import pygal
from pygal.style import CleanStyle
import numpy as np
import gdata
from youtube.models import Video
from youtube.models import Category
from youtube.models import Comment
from django.utils import dateparse
import cProfile
import pylab as pl
from sklearn import linear_model

from collections import Counter

# Create your views here.

def index(request):
    popular = util.getMostPopularVideos()
    #date = [entry.published.text.split('T')[0] for entry in popular.entry]
    return render(request, 'youtube/index.html', {'popular': popular})

def about(request):
    return render(request, 'youtube/about.html')

def video(request, video_id):

    if Video.objects.filter(id=video_id).exists():
        video = Video.objects.get(id=video_id)

    else:


        yt_service = gdata.youtube.service.YouTubeService()

        try:
            video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        except gdata.service.RequestError, inst:
            error = inst[0]
            context = {'video_id': video_id, 'error': error}
            return render(request, 'youtube/video.html', context)

        category = Category.objects.get_or_create(id=video_details.media.category[0].text)

        rating = 0

        if video_details.rating.average:
            rating = (float(video_details.rating.average) - float(video_details.rating.min)) / (float(video_details.rating.max)-1)
            print "video percent rating: {}".format(rating)

        print video_details.statistics.view_count


        video , new = Video.objects.get_or_create(id=video_id,
                                                  category=category[0],
                                                  title=video_details.media.title.text,
                                                  rating=rating,
                                                  date=dateparse.parse_datetime(video_details.published.text),
                                                  image=video_details.media.thumbnail[0].url,
                                                  view_count=video_details.statistics.view_count,
                                                )

    context = {'video_id': video_id, 'video': video}
    return render(request, 'youtube/video.html', context)

def report(request, video_id):

    video_obj = Video.objects.get(id=video_id)

    if not Comment.objects.filter(video=video_obj).exists():
        latest_question_list = util.getComments(video_id)
        cProfile.runctx('util.savecomments(latest_question_list, video_id)', globals(), locals())
        #util.savecomments(latest_question_list, video_id)


    comments = Comment.objects.filter(video=video_obj)

    positive_count = Comment.objects.filter(video=video_obj,afinn_score__gt=0).count()
    negative_count = Comment.objects.filter(video=video_obj,afinn_score__lt=0).count()
    video_obj.score = positive_count/(positive_count+negative_count)
    video_obj.save()

    comments = Comment.objects.filter(video=video_obj)
    score_list = comments.values_list('afinn_score',flat=True)

    afinn_score_list = np.array(score_list)

    chart_data = np.histogram(afinn_score_list, range=(-5.5, 5.5), bins=11, density=True)[0] * 100

    charts =[]

    bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True)
    bar_chart.x_labels = map(str, range(-5, 6))
    bar_chart.y_labels = map(str, range(0, 110, 10))
    bar_chart.add('Comment Sentiment', chart_data)

    charts.append(bar_chart)

    pie_chart = pygal.Pie(style=CleanStyle, disable_xml_declaration=True)
    pie_chart.title = 'Browser usage in February 2012 (in %)'
    pie_chart.add('Positive', positive_count)
    pie_chart.add('Negative', negative_count)

    charts.append(pie_chart)

    data = []
    cat_chart = pygal.XY(title=u'Sentiment vs Rating based on category', range=(0,1),
                         style=CleanStyle, disable_xml_declaration=True, stroke=False,
                         xlabel='Sentiment score', ylabel='Youtube rating')
    cat_chart.title = 'Sentiment vs Rating based on category'
    for c in Category.objects.all():
        temp_list = [(v.score, v.rating) for v in Video.objects.filter(category=c)]
        data += temp_list
        cat_chart.add( c.id, temp_list)
    charts.append(cat_chart)

    # scores = np.array(zip(*data)[0])
    # scores_w_intercept = np.array([np.ones( len(scores) ), scores]).T
    # ratings = np.array(zip(*data)[1])
    # regr = linear_model.LinearRegression(fit_intercept=False)
    # regr.fit(scores_w_intercept, ratings)
    # coef = regr.coef_
    # lin_reg = pl.figure(title=u'Linear regression on the data', xlabel='Sentiment score', ylabel='Youtube rating')
    # pl.title('Linear regression on the data')
    # pl.scatter(scores, ratings, marker='x')
    # pl.xlabel('Sentiment score')
    # pl.ylabel('Youtube rating')
    # x = np.linspace(0, max(scores), 20)
    # y = x*coef[1]+coef[0]
    # pl.plot(x, y)
    # charts.append(cat_chart)

    # latest_question_list = util.getComments(video_id)
    #
    # util.savecomments(latest_question_list, video_id)
    #
    # print "number of comments analysed {}".format(len(latest_question_list))
    # afinn_score = np.array([util.afinn_sentiment(text.content.text) for text in latest_question_list])
    #
    # print "positive comments: {0}".format((afinn_score > 0).sum())
    # print "negative comments: {0}".format((afinn_score < 0).sum())
    #
    # charts =[]
    #
    # pie_chart = pygal.Pie(style=CleanStyle, disable_xml_declaration=True)
    # pie_chart.title = 'Browser usage in February 2012 (in %)'
    # pie_chart.add('Possitive', (afinn_score > 0).sum())
    # pie_chart.add('Negative', (afinn_score < 0).sum())
    #
    # charts.append(pie_chart)
    #
    # #labmt_score = np.array([util.labmt_sentiment(text.content.text) for text in latest_question_list])
    #
    # chart_data = np.histogram(afinn_score, range=(-5.5,5.5), bins=11, density=True)[0] * 100
    #
    # bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True)
    # bar_chart.x_labels = map(str, range(-5, 6))
    # bar_chart.y_labels = map(str, range(0, 110, 10))
    # bar_chart.add('Comment Sentiment', chart_data)
    #
    # charts.append(bar_chart)
    # # for entry in latest_question_list:
    # #     Comment(id=entry,author=,video_id=,text=afinn_score=,labmt_score=)
    #
    #context = {'video_id': video_id, 'result': latest_question_list, 'charts': charts}

    context = {'video_id': video_id, 'result': comments, 'charts': charts}

    return render(request, 'youtube/report.html', context)


def search(request):
    error = False

    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            result = util.searchresult(q)
            print len(result)
            return render(request, 'youtube/search.html', {'result': result, 'query': q})

    return render(request, 'search_form.html', {'error': error, 'query': q})




