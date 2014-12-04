# Tests for util.py
# 94% lines of cover
import unittest
import util
import coverage

class UtilTestCase(unittest.TestCase):

    def test_positive_afinn(self):
        text = "Weather is fantastic"
        sentimentValue = util.afinn_sentiment(text)
        self.assertGreater(sentimentValue, 0, "sentiment")

    def test_negative_sentiment(self):
        text = "Weather is bad"
        sentimentValue = util.afinn_sentiment(text)
        self.assertLess(sentimentValue,0,"sentiment")

    def test_neutral_sentiment(self):
        text = "this is an abstract comment"
        sentimentValue = util.afinn_sentiment(text)
        self.assertAlmostEquals(sentimentValue,0,"sentiment")

    # TODO Fix the sentiment values in labsentiment
    def test_positive_labmt(self):
        text = "Weather is fantastic"
        sentimentValue = util.labmt_sentiment(text)
        self.assertGreater(sentimentValue, 5, "sentiment")

    # TODO Fix the sentiment values in labsentiment
    def test_negative_labmtt(self):
        text = "Weather is bad"
        sentimentValue = util.labmt_sentiment(text)
        self.assertLess(sentimentValue,5,"sentiment")

    def test_neutral_labmt(self):
        text = "this is an abstract comment"
        sentimentValue = util.labmt_sentiment(text)
        self.assertAlmostEquals(sentimentValue,5,"sentiment")

    def test_validId_getComments(self):
        videoid = "BpPMvttgOuY"
        comments = util.get_comments(videoid,1,10)
        self.assertGreater(comments.__sizeof__(),0)

    def test_commentsDisabled_getComments(self):
        videoid = "v-g2UKEQ-Y4"
        comments = util.get_comments(videoid,1,10)
        self.assertEqual(comments.__sizeof__(),0)

    # TODO It is supposed to get no results but it doesn't
    def test_noResults_searchresult(self):
        search_query = "dsafafsfafqfwceththfehrh"
        feed = util.searchresult(search_query,1)
        self.assertEqual(feed.__sizeof__(),0)

if __name__ == '__main__':
    unittest.main()
