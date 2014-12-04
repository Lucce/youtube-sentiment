from django.conf.urls import patterns, include, url
from youtube import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^video/(?P<video_id>[\w\-]+)/$', views.video, name='video'),
    url(r'^report/(?P<video_id>[\w\-]+)/$', views.report, name='prut'),
    url(r'^regressive_analysis/$', views.regressive_analysis, name='stats'),
    url(r'^search/$', views.search, name='search'),
)