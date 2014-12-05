from django.conf.urls import patterns, url

from youtube import views


urlpatterns = patterns('',

    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^video/(?P<video_id>[\w\-]+)/$', views.video, name='video'),
    url(r'^videos/(?P<video1>[\w\-]+)/(?P<video2>[\w\-]+)/$', views.videos, name='videos'),
    url(r'^com/(?P<video1>[\w\-]+)/(?P<video2>[\w\-]+)/$', views.compare, name='compare'),
    url(r'^report/(?P<video_id>[\w\-]+)/$', views.report, name='prut'),
    url(r'^regressive_analysis/$', views.regressive_analysis, name='stats'),
    url(r'^search/$', views.search, name='search'),
)