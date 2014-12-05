from django import template
from django.template.defaultfilters import stringfilter
from django.utils import dateparse

from youtube import util


register = template.Library()

@register.filter(name='getid')
@stringfilter
def getid(value):
    return value.split("/")[-1]

@register.filter(name='getdate')
@stringfilter
def getdate(text):
    # return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%Y %H:%M:%S")
    return dateparse.parse_datetime(text)

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

@register.filter(name='percent')
@stringfilter
def percent(decimal):
    return float(decimal) * 100


@register.inclusion_tag('youtube/tagtemplate/test.html')
def show_progress(number):
    return {'number': number}


@register.inclusion_tag('youtube/tagtemplate/searchform.html', takes_context=True)
def get_search(context):
    return context