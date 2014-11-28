from django.shortcuts import render
from youtube import video
from youtube import util
from youtube.models import Comment
import pygal
from pygal.style import CleanStyle
import numpy as np
import gdata
from collections import Counter

# Create your views here.

def index(request):

    return render(request, 'youtube/index.html')

def video(request, video_id):

    yt_service = gdata.youtube.service.YouTubeService()

    video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)

    # latest_question_list = util.getComments(video_id)
    # afinn_score = np.array([util.afinn_sentiment(text.content.text) for text in latest_question_list])
    #
    # #labmt_score = np.array([util.labmt_sentiment(text.content.text) for text in latest_question_list])
    #
    # chart_data = np.histogram(afinn_score, range=(-5.5,5.5), bins=11, density=True)[0] * 100
    #
    # bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True)
    # bar_chart.x_labels = map(str, range(-5, 6))
    # bar_chart.y_labels = map(str, range(0, 110, 10))
    #
    # bar_chart.add('Comment Sentiment', chart_data)

    # for entry in latest_question_list:
    #     Comment(id=entry,author=,video_id=,text=afinn_score=,labmt_score=)

    #context = {'video_id': video_id, 'result': latest_question_list, 'video' : video_details, 'chart': bar_chart}

    horizontalbar_chart = pygal.HorizontalBar(disable_xml_declaration=True)
    horizontalbar_chart.title = 'Browser usage in February 2012 (in %)'
    horizontalbar_chart.add('IE', 19.5)
    horizontalbar_chart.add('Firefox', 36.6)
    horizontalbar_chart.add('Chrome', 36.3)
    horizontalbar_chart.add('Safari', 4.5)
    horizontalbar_chart.add('Opera', 2.3)

    context = {'video_id': video_id,'video': video_details, 'testchart': horizontalbar_chart }
    return render(request, 'youtube/video.html', context)

def report(request, video_id):

    latest_question_list = util.getComments(video_id)
    print "number of comments analysed {}".format(len(latest_question_list))
    afinn_score = np.array([util.afinn_sentiment(text.content.text) for text in latest_question_list])

    print "positive comments: {0}".format((afinn_score > 0).sum())
    print "negative comments: {0}".format((afinn_score < 0).sum())

    charts =[]

    pie_chart = pygal.Pie(style=CleanStyle, disable_xml_declaration=True)
    pie_chart.title = 'Browser usage in February 2012 (in %)'
    pie_chart.add('Possitive', (afinn_score > 0).sum())
    pie_chart.add('Negative', (afinn_score < 0).sum())

    charts.append(pie_chart)

    #labmt_score = np.array([util.labmt_sentiment(text.content.text) for text in latest_question_list])

    chart_data = np.histogram(afinn_score, range=(-5.5,5.5), bins=11, density=True)[0] * 100

    bar_chart = pygal.Bar(title=u'Afinn sentiment Histrogram', range=(0, 100), style=CleanStyle, disable_xml_declaration=True)
    bar_chart.x_labels = map(str, range(-5, 6))
    bar_chart.y_labels = map(str, range(0, 110, 10))
    bar_chart.add('Comment Sentiment', chart_data)

    charts.append(bar_chart)
    # for entry in latest_question_list:
    #     Comment(id=entry,author=,video_id=,text=afinn_score=,labmt_score=)

    context = {'video_id': video_id, 'result': latest_question_list, 'charts': charts}
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




