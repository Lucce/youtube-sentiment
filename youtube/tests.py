from datetime import date

from django.test import TestCase
import gdata

import util
from youtube.models import Video
from youtube.models import Comment
from youtube.models import Category


""" Functionality testing """


class UtilTestCase(TestCase):
    def setUp(self):
        """ Database initialization """
        date1 = date(2012, 9, 27)

        category1 = Category(id="Tech")
        category2 = Category(id="Entertainment")
        category3 = Category(id="Film")
        category4 = Category(id="Games")
        category5 = Category(id="People")

        category1.save()
        category2.save()
        category3.save()
        category4.save()
        category5.save()

        video1 = Video(id="znK652H6yQM",
                       title="iPhone 6 Plus Bend Test",
                       rating="0.88134885",
                       date=date1,
                       image="https://i.ytimg.com/vi/znK652H6yQM/0.jpg",
                       view_count="58918265",
                       category_id="Tech",
                       score="0.494791666666667")

        video2 = Video(id="zhFmv6e3E5Y",
                       title="Portland State player fakes handshake, steals ball, dunks it.",
                       rating="0.564516125",
                       date=date1,
                       image="https://i.ytimg.com/vi/zhFmv6e3E5Y/0.jpg",
                       view_count="574677",
                       category_id="Film",
                       score="0.405405405405405")

        video3 = Video(id="yz_pX8Q32Rs",
                       title="Insomnia- Faithless",
                       rating="0.9878049",
                       date=date1,
                       image="https://i.ytimg.com/vi/yz_pX8Q32Rs/0.jpg",
                       view_count="10604",
                       category_id="Film",
                       score="0.25")
        video1.save()
        video2.save()
        video3.save()

        comment1 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z13cvvjodlzkin03523mevfokmixerzy004",
            author="badboyson12",
            video_id="XI8o6s1pmwg",
            text="come on he rocks",
            date=date1,
            afinn_score="0.0")
        comment2 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z12ri1ypmm2ryzwhd04cjprx5znbdlwh34o",
            author="Cathy Wood",
            video_id="XI8o6s1pmwg",
            text="I love Seths laugh",
            date=date1,
            afinn_score="2.0")
        comment3 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z12xyxgg2ovrvv3x304cdlvarvuwu5z5ts40k",
            author="samantha jones",
            video_id="XI8o6s1pmwg",
            text="Seth Rogens yields ",
            date=date1,
            afinn_score="0.577350269189626")
        comment4 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z12ijfigqofty35mo235iv3zmofcsrcu1",
            author="Arden Anastasi",
            video_id="XI8o6s1pmwg",
            text="Seth Rogen is such a nice, cool guy. Hate him",
            date=date1,
            afinn_score="2.21359436211787")
        comment5 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z12ddfxosmzxwnxhy04cfnsocoyexfgwvxw0k",
            author="TheWassag",
            video_id="yz_pX8Q32Rs",
            text="cool cool cool",
            date=date1,
            afinn_score="2.21359436211787")
        comment6 = Comment(
            id="http://gdata.youtube.com/feeds/api/videos/XI8o6s1pmwg/comments/z13jghua1yjyfrbde23oczfxuxjwevim4",
            author="Munashige Sama",
            video_id="yz_pX8Q32Rs",
            text="Like the positive energy, like,like,like",
            date=date1,
            afinn_score="2.21359436211787")
        comment1.save()
        comment2.save()
        comment3.save()
        comment4.save()
        comment5.save()
        comment6.save()

    def test_category_view(self):
        """ test_category_view should results 1 record from the db with id = 'Tech'   """
        cat = Category.objects.get(id="Tech")
        self.assertEquals("Tech", cat.id)

    def test_video_view(self):
        """ test_video_view should results 2 records from the db with category_id=''   """
        video = Video.objects.filter(category_id="Film")
        self.assertEquals(2, len(video))

    def test_comment_view(self):
        com = Comment.objects.filter(video_id="XI8o6s1pmwg")
        self.assertEquals(4, len(com))

    def test_save_video(self):
        """ test_save_video should results 'Enterntainment' from the database from a video  """
        video = util.save_video('XI8o6s1pmwg')
        self.assertEquals("Entertainment", str(video.category))

    def test_save_video_raise_exc(self):
        """ test_save_video_raise_exc should raise a gdata.service.RequestError exception """
        self.assertRaises(gdata.service.RequestError, util.save_video, 'aaaaaaaaaaaaaaa')

    def test_afinn_sentiment_positive(self):
        """ test_afinn_sentiment_positive should results a value greater than 0 for a positive comment """
        comment = "Weather is fantastic"
        sentiment_value = util.afinn_sentiment(comment)
        self.assertGreater(sentiment_value, 0, "sentiment")

    def test_afinn_sentiment_negative(self):
        """ test_afinn_sentiment_negative should results a value less than 0 for a negative comment """
        comment = "Weather is bad"
        sentiment_value = util.afinn_sentiment(comment)
        self.assertLess(sentiment_value, 0, "sentiment")

    def test_afinn_sentiment_neutral(self):
        """ test_afinn_sentiment_neutral should results a value close to 0 for a neutral comment """
        comment = "this is an abstract comment"
        sentiment_value = util.afinn_sentiment(comment)
        self.assertAlmostEquals(sentiment_value, 0, "sentiment")

    def test_get_comments_valid_id(self):
        """ test_get_comments_valid_id should results a NON zero list for a valid video id that contains comments """
        comments = util.get_comments('XI8o6s1pmwg')
        self.assertGreater(len(comments), 0)

    def test_get_comments_disabled(self):
        """ test_get_comments_disabled should results a zero list for a valid video id with disabled comments """
        comments = util.get_comments('v-g2UKEQ-Y4')
        self.assertEqual(len(comments), 0)

    def test_create_frequency_list_without_frequency(self):
        """ test_create_frequency_list should results a zero list """
        comments = Comment.objects.filter(video="XI8o6s1pmwg")
        self.assertEquals(0, len(util.create_frequency_list(comments)))

    def test_create_frequency_list_with_frequency(self):
        """ test_create_frequency_list should results a list greater than 0 """
        comments = Comment.objects.filter(video_id="yz_pX8Q32Rs")
        self.assertGreater(len(util.create_frequency_list(comments)), 0)

    def test_video_charts(self):
        """ test_video_charts should results a list of charts with length greater than 0 """
        video_id = "znK652H6yQM"
        video_obj = Video.objects.get(id=video_id)

        comments = Comment.objects.filter(video_id="znK652H6yQM")
        self.assertGreater(len(util.video_charts(video_obj, comments)), 0)

    def test_get_most_popular(self):
        """ test_get_most_popular should results a list of videos with length greater than 0 """
        feed = util.get_most_popularvideos()
        self.assertGreater(len(feed), 0)

    def test_search_result_fail(self):
        """ test_search_result_fail should results a zero list of videos, no videos matching the search criteria """
        feed = util.searchresult('Thisisabigstringtofailthesearchresultsmethod')
        self.assertEqual(len(feed), 0)

    def test_search_result_pass(self):
        """ test_search_result_pass should results list of videos with length greater than 0 """
        search_query = "Michael Jordan"
        feed = util.searchresult(search_query)
        self.assertGreater(len(feed), 0)

    def test_get_total_data_pass(self):
        """
            test_get_total_data_pass should results a dict of the categories
            and their total score and data with length  greater than 0
        """
        data_dict = util.get_total_data()
        self.assertGreater(len(data_dict), 0)

    def test_get_total_data_correct_keys(self):
        """ test_get_total_data_pass should results a dict of the categories with including keys Music,Tech """
        data_dict = util.get_total_data()
        self.assertEquals(True, "Film" in data_dict)

    def test_get_total_data_false_keys(self):
        """ test_get_total_data_pass 'History' is supposed NOT to be a category in the dictionary """
        data_dict = util.get_total_data()
        self.assertEquals(False, "History" in data_dict)

    def test_category_chart(self):
        """ test_category_chart should results a chart that is not none """
        data_dict = util.get_total_data()
        self.assertIsNotNone((util.category_chart(data_dict)))