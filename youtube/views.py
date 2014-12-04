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
    return render(request, 'youtube/index.html', {'popular': popular})

def about(request):
    return render(request, 'youtube/about.html')

def video(request, video_id):

    if Video.objects.filter(id=video_id).exists():
        video = Video.objects.get(id=video_id)

    else:
        video = util.save_video(video_id)

    context = {'video_id': video_id, 'video': video}
    return render(request, 'youtube/video.html', context)

def report(request, video_id):

    video_obj = Video.objects.get(id=video_id)

    if not Comment.objects.filter(video=video_obj).exists():
        latest_question_list = util.getComments(video_id)
        cProfile.runctx('util.savecomments(latest_question_list, video_id)', globals(), locals())
        #util.savecomments(latest_question_list, video_id)

    comments = Comment.objects.filter(video=video_obj)

    charts = util.video_charts(video_obj, comments)

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
            return render(request, 'youtube/search.html', {'result': result, 'query': q})

    return render(request, 'search_form.html', {'error': error, 'query': q})




