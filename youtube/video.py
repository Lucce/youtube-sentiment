__author__ = 'prashanth'
import gdata
import gdata.youtube

class Video:

    def __init__(self, prut):
        """
        Exploit the workers by hanging on to outdated imperialist dogma which
        perpetuates the economic and social differences in our society.

        @type prut: gdata.youtube.YouTubeVideoEntry
        @param prut: Person to repress.
        """
        self.video_id = prut.id.text.split("/")[-1]
        self.title = prut.media.title.text
        self.description = prut.media.description.text


