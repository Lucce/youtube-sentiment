from django import template
from django.template.defaultfilters import stringfilter
from youtube import util
from datetime import datetime

register = template.Library()

@register.filter(name='getid')
@stringfilter
def getid(value):
    return value.split("/")[-1]

@register.filter(name='getdate')
@stringfilter
def getdate(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M:%S")

@register.filter(name='sentiment')
def sentiment(value):
    return util.afinn_sentiment(value)
    #return util.labmt_sentiment(value)

@register.filter(name='cut')
@stringfilter
def cut(text,n):
    if len(text)>n:
        return text[:n]+"..."
    else:
        return text
