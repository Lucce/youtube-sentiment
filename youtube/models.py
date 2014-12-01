from django.db import models

# Create your models here.

class Category(models.Model):

    id = models.CharField(primary_key=True, unique=True, max_length=20)

    def __unicode__(self):
        return self.id

class Video(models.Model):

    id = models.CharField(max_length=20, primary_key=True, unique=True)
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=30)
    rating = models.FloatField(blank=True)
    date = models.DateTimeField()
    image = models.URLField()
    view_count = models.IntegerField()

    def __unicode__(self):
        return self.id

class Comment(models.Model):

    id = models.URLField(primary_key=True, unique=True)
    author = models.CharField(max_length=30)
    video = models.ForeignKey(Video)
    text = models.TextField()
    date = models.DateTimeField()
    afinn_score = models.FloatField(null=True)
    #labmt_score = models.FloatField()

    def __unicode__(self):
        return self.text

