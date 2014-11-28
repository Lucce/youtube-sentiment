from __future__ import unicode_literals
__author__ = 'prashanth'
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import gdata.youtube
import gdata.youtube.service
import nltk
import numpy as np

test2 = u'this\ufeff'
print type(test2)
print test2
print test2.replace('\ufeff',"")

test = np.random.uniform(-5, 5, size=10)

print test
print np.histogram(test,bins=11,range=(-5.0,5.0))
# yt_service = gdata.youtube.service.YouTubeService()
#
# comment_feed_link = "http://gdata.youtube.com/feeds/api/videos/{id}/comments?start-index={index}&max-results=10&orderby=published".format
#
# url = comment_feed_link(id='6vopR3ys8Kw', index=1)
# print url
#
# comment_feed = yt_service.GetYouTubeVideoCommentFeed(url).entry
#
# text = comment_feed[0].content.text
# #text = unicode(comment_feed[0].content.text).strip()
#
# #text = comment_feed[0].content.text.decode('utf-8').strip()
#
#
# print type(text)
# print text
# test = nltk.word_tokenize(text.strip())
# print type(test[-1])
# test2 = np.array(test)
# test2 = np.char.decode(test2, encoding='utf-8', errors='strict')
# print len(nltk.word_tokenize(text.strip()))
#
# print test2
# print test2[3].rstrip()
#
# url = comment_feed_link(id='QnBscNAF4pg', index=1)
# print url
#
# comment_feed = yt_service.GetYouTubeVideoCommentFeed(url).entry
# text = comment_feed[4].content.text
#
# print type(text)
# print text
# print np.char.decode(text, encoding='utf-8-sig', errors='strict')
# print nltk.word_tokenize(text.strip())
# print len(nltk.word_tokenize(text.strip()))


