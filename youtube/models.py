from django.db import models

# Create your models here.
class Comment(models.Model):

    id = models.URLField(primary_key=True, unique=True)
    author = models.CharField(max_length=30)
    video_id = models.CharField(max_length=10)
    text = models.TextField()
    afinn_score = models.FloatField()
    labmt_score = models.FloatField()

    def __unicode__(self):
        return self.text

