from django.conf.urls import patterns, include, url
from youtube import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^video/(?P<video_id>[\w\-]+)/$', views.video, name='video'),
    url(r'^report/(?P<video_id>[\w\-]+)/$', views.report, name='prut'),
    url(r'^search/$', views.search, name='search'),
)