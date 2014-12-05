from __future__ import division

import os

from django.shortcuts import render
import gdata
from django.utils.html import escape
from pytagcloud import create_tag_image
from django.conf import settings

from youtube import util
from youtube.models import Video
from youtube.models import Comment




# Create your views here.


def index(request):
    popular = util.get_most_popularvideos()
    return render(request, 'youtube/index.html', {'popular': popular})


def about(request):
    return render(request, 'youtube/about.html')


def video(request, video_id):

    if Video.objects.filter(id=video_id).exists():
        video_obj = Video.objects.get(id=video_id)
    else:
        try:
            video_obj = util.save_video(video_id)
        except gdata.service.RequestError, inst:

            context = {'error': inst[0]}
            return render(request, 'youtube/error.html', context)

    context = {'video_id': video_id, 'video': video_obj}
    return render(request, 'youtube/video.html', context)


def videos(request, video1, video2):

    if Video.objects.filter(id=video1).exists():
        video_1 = Video.objects.get(id=video1)
    else:
        try:
            video1 = util.save_video(video_1)
        except gdata.service.RequestError, inst:
            context = {'error': inst[0], 'id': video1}
            return render(request, 'youtube/error.html', context)

    if Video.objects.filter(id=video2).exists():
        video_2 = Video.objects.get(id=video2)
    else:
        try:
            video_2 = util.save_video(video2)
        except gdata.service.RequestError, inst:
            context = {'error': inst[0], 'id': video2}
            return render(request, 'youtube/error.html', context)


    context = {'video1': video_1, 'video2': video_2}
    return render(request, 'youtube/videos.html', context)


def compare(request, video1, video2):
    # if Video.objects.filter(id=video1).exists():
    video_1 = Video.objects.get(id=video1)

    if not Comment.objects.filter(video=video1).exists():
        latest_question_list = util.get_comments(video1)
        util.savecomments(latest_question_list, video1)
        video_1 = Video.objects.get(id=video1)

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

    path = os.path.join(settings.STATIC_PATH, 'youtube', 'tagcloud', '{0}.png'.format(video_id))
    create_tag_image(tags, path, size=(600, 450))

    context = {'video_id': video_id, 'result': comments, 'charts': charts}

    return render(request, 'youtube/report.html', context)


def regressive_analysis(request):
    cat_data = util.get_total_data()
    chart = util.category_chart(cat_data)
    image = util.linear_regression(cat_data)
    return render(request, 'youtube/regressive_analysis.html', {'chart': chart, 'image': image})


def search(request):
    error = False
    page = 1
    sort = 'relevance'

    if 'q' in request.GET:
        q = request.GET['q']

        if not q:
            error = True
        else:

            if 'page' in request.GET:
                try:
                    page = int(request.GET['page'])
                    if page > 20:
                        page = 1
                except ValueError:
                    page = 1

            if 'sort' in request.GET:
                sorting = escape(request.GET['sort'])
                if sorting in ['viewCount', 'published', 'relevance', 'rating']:
                    sort = sorting

            result = util.searchresult(q, page=page, sort=sort)

            context = {'result': result, 'query': q, 'page': page, 'sort': sort}

            url = "?q={query}&sort={sort}".format(query=q, sort=sort)

            if 'compare' in request.GET:

                url += "&compare=on"

                context['compare'] = request.GET['compare']

                if 'video1' in request.GET:
                    context['video1'] = escape(request.GET['video1'])
                    url += "&video1={}".format(context['video1'])
                if 'video2' in request.GET:
                    context['video2'] = escape(request.GET['video2'])

                context['link'] = url

                if 'video1' in request.GET and 'video2' in request.GET:
                    context = {'video1': context['video1'], 'video2': context['video2']}
                    return render(request, 'youtube/compare.html', context)

            context['link'] = url
            return render(request, 'youtube/search.html', context)

    return render(request, 'search_form.html', {'error': error})