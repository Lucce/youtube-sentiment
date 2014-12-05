from django.test import TestCase
import gdata
import util
from youtube.models import Video
from youtube.models import Comment


""" Functionality testing """


class UtilTestCase(TestCase):
    def test_get_wordlist(self):
        self.assertGreater(len(util.get_wordlist()), 0)

    def test_save_video(self):
        video = util.save_video('XI8o6s1pmwg')
        self.assertEquals("Entertainment", str(video.category))

    def test_save_video_exc(self):
        self.assertRaises(gdata.service.RequestError, util.save_video, 'aaaaaaaaaaaaaaa' )

    def test_positive_afinn(self):
        text = "Weather is fantastic"
        sentimentValue = util.afinn_sentiment(text)
        self.assertGreater(sentimentValue, 0, "sentiment")

    def test_negative_sentiment(self):
        text = "Weather is bad"
        sentimentValue = util.afinn_sentiment(text)
        self.assertLess(sentimentValue, 0, "sentiment")

    def test_neutral_sentiment(self):
        text = "this is an abstract comment"
        sentimentValue = util.afinn_sentiment(text)
        self.assertAlmostEquals(sentimentValue, 0, "sentiment")

    def test_get_comments_valid_id(self):
        comments = util.get_comments('BpPMvttgOuY')
        self.assertGreater(comments.__sizeof__(), 0)

    def test_get_comments_disabled(self):
        comments = util.get_comments('v-g2UKEQ-Y4')
        self.assertEqual(len(comments), 0)

    def test_video_charts(self):
        video_obj = Video.objects.filter(category_id='Tech')
        # video_id = "t_77GeNEzFQ"
        # video_obj = Video.objects.get(id=video_id)
        print video_obj[1]
        #comments = Comment.objects.filter(video_id="uirZ0bDzoYQ")
        #self.assertGreater(len(util.video_charts(video_obj, comments)), 0)

    def test_get_most_popular(self):
        feed = util.get_most_popularvideos()
        self.assertGreater(len(feed), 0)

    def test_search_result_fail(self):
        feed = util.searchresult('Thisisabigstringtofailthesearchresultsmethod')
        self.assertEqual(len(feed), 0)

    def test_search_result_pass(self):
        search_query = "Michael Jordan"
        feed = util.searchresult(search_query)
        self.assertGreater(len(feed), 0)

        # def setUp(self):
        #
        # video_id = "jofNR_WkoCE"
        #
        # yt_service = gdata.youtube.service.YouTubeService()
        #     video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        #     print video_details.author.name
        #     test, temp_cat = Category.objects.get_or_create(id=video_details.media.category[0].text)
        #
        #     testobj = Video.objects.get_or_create(id=video_id, category=test)
        #
        #     video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        #
        #     data = util.get_comments(video_id)
        #
        #     util.savecomments(data, video_id)

        # def test_animals_can_speak(self):
        #     """Animals that can speak are correctly identified"""
        #
        #     lion = Video.objects.get(id="jofNR_WkoCE")
        #
        #     # test = Comment.objects.filter(video=lion)
        #     #
        #     # Category.objects.get(id="Entertainment")
        #     #
        #     # Category.objects.filter(id="Entertainment")
        #     #
        #     # for com in test:
        #     #     print com.text

        #cat = Animal.objects.get(name="cat")
        #self.assertEqual(lion.speak(), 'The lion says "roar"')
        #self.assertEqual(cat.speak(), 'The cat says "meow"')