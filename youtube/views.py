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
from django.utils.html import escape
from django.utils import dateparse
import cProfile
import pylab as pl
from sklearn import linear_model
from pytagcloud import create_tag_image
from django.conf import settings

from collections import Counter

# Create your views here.

def index(request):
    popular = util.getMostPopularVideos()
    return render(request, 'youtube/index.html', {'popular': popular})

def about(request):
    return render(request, 'youtube/about.html')

def video(request, video_id):

    if Video.objects.filter(id=video_id).exists():
        video = Video.objects.get(id=video_id)

    else:
        try:
            video = util.save_video(video_id)
        except gdata.service.RequestError, inst:
            context = {'error': inst[0]}
            return render(request, 'youtube/error.html', context)

    context = {'video_id': video_id, 'video': video}
    return render(request, 'youtube/video.html', context)


def videos(request, video1, video2):
    if Video.objects.filter(id=video1).exists():
        video_1 = Video.objects.get(id=video1)
    else:
        video_1 = util.save_video(video1)

    if Video.objects.filter(id=video2).exists():
        video_2 = Video.objects.get(id=video2)
    else:
        video_2 = util.save_video(video2)

    context = {'video1': video_1, 'video2': video_2}
    return render(request, 'youtube/videos.html', context)


def compare(request, video1, video2):
    # if Video.objects.filter(id=video1).exists():
    video_1 = Video.objects.get(id=video1)

    if not Comment.objects.filter(video=video1).exists():
        latest_question_list = util.get_comments(video1)
        util.savecomments(latest_question_list, video1)
        video_1 = Video.objects.get(id=video1)

    #if Video.objects.filter(id=video2).exists():
    video_2 = Video.objects.get(id=video2)
    if not Comment.objects.filter(video=video2).exists():
        latest_question_list = util.get_comments(video2)
        util.savecomments(latest_question_list, video2)
        video_2 = Video.objects.get(id=video2)

    context = {'video1': video_1, 'video2': video_2}
    return render(request, 'youtube/compare.html', context)

def report(request, video_id):

    video_obj = Video.objects.get(id=video_id)

    if not Comment.objects.filter(video=video_obj).exists():
        latest_question_list = util.get_comments(video_id)
        util.savecomments(latest_question_list, video_id)
        video_obj = Video.objects.get(id=video_id)

    comments = Comment.objects.filter(video=video_obj)

    charts = util.video_charts(video_obj, comments)

    frequency_list = util.create_frequency_list(comments)
    tags = util.tag_them(frequency_list, maxsize=120)
    create_tag_image(tags, settings.STATIC_PATH_WINDOWS+'\images\cloud.png', size=(600, 450))
    # create_html_data(tags, size=(900, 600))

    context = {'video_id': video_id, 'result': comments, 'charts': charts}

    return render(request, 'youtube/report.html', context)

def regressive_analysis(request):

    chart = util.total_charts()
    return render(request, 'youtube/regressive_analysis.html', {'chart': chart})

def search(request):
    error = False

    if 'q' in request.GET:
        q = request.GET['q']
        if not q:
            error = True
        else:
            result = util.searchresult(q)
            return render(request, 'youtube/search.html', {'result': result, 'query': q})

            context = {'result': result, 'query': q}

            if 'compare' in request.GET:

                url = "?q={}&compare=on".format(q)

                context['compare'] = request.GET['compare']

                if 'video1' in request.GET:
                    context['video1'] = escape(request.GET['video1'])
                    url += "%video1={}".format(context['video1'])
                if 'video2' in request.GET:
                    context['video2'] = escape(request.GET['video2'])

                print url

                context['link'] = url

                if 'video1' in request.GET and 'video2' in request.GET:
                    context = {'video1': context['video1'], 'video2': context['video2']}
                    return render(request, 'youtube/compare.html', context)

            return render(request, 'youtube/search.html', context)

    return render(request, 'search_form.html', {'error': error})




