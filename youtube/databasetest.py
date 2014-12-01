from django.utils import dateparse
import gdata.youtube.service
import gdata
gdata.service.RequestError
import sys

print dateparse.parse_datetime("2011-11-11T18:37:24.000Z")

yt_service = gdata.youtube.service.YouTubeService()

try:
  video_details = yt_service.GetYouTubeVideoEntry(video_id="l6lYFO_tKlE")
except gdata.service.RequestError, inst:
  response = inst[0]
  print response
  status = response['status']
  reason = response['reason']
  body = response['body']
  # Handle the error here

print "test"
print video_details