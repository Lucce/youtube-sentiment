from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^youtube/', include('youtube.urls')),
)
