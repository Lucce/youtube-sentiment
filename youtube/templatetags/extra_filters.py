from django import template
from django.template.defaultfilters import stringfilter
from youtube import util

register = template.Library()

@register.filter(name='getid')
@stringfilter
def getid(value):
    return value.split("/")[-1]

@register.filter(name='getdate')
@stringfilter
def getdate(value):

    return value.split("T")[0]

@register.filter(name='sentiment')
def sentiment(value):
    return util.afinn_sentiment(value)
    #return util.labmt_sentiment(value)