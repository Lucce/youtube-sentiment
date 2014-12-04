from django.test import TestCase
from youtube.models import Video
from youtube.models import Category
from youtube.models import Comment
import util
import gdata

# Create your tests here.
class AnimalTestCase(TestCase):
    def setUp(self):

        video_id = "jofNR_WkoCE"

        yt_service = gdata.youtube.service.YouTubeService()
        video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)
        print video_details.author.name
        test, temp_cat = Category.objects.get_or_create(id=video_details.media.category[0].text)

        testobj = Video.objects.get_or_create(id=video_id, category=test)

        video_details = yt_service.GetYouTubeVideoEntry(video_id=video_id)

        data = util.get_comments(video_id)

        util.savecomments(data, video_id)

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""

        lion = Video.objects.get(id="jofNR_WkoCE")

        # test = Comment.objects.filter(video=lion)
        #
        # Category.objects.get(id="Entertainment")
        #
        # Category.objects.filter(id="Entertainment")
        #
        # for com in test:
        #     print com.text

        #cat = Animal.objects.get(name="cat")
        #self.assertEqual(lion.speak(), 'The lion says "roar"')
        #self.assertEqual(cat.speak(), 'The cat says "meow"')