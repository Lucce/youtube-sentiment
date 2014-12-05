from django import template
from django.template.defaultfilters import stringfilter
from django.utils import dateparse

from youtube import util


register = template.Library()


@register.filter(name='getid')
@stringfilter
def getid(value):
    """
    Outputs the last part of the input string after the /
    
    """
    return value.split("/")[-1]


@register.filter(name='getdate')
@stringfilter
def getdate(text):
    """
    Converts youtube dateformat to datetime.datetime object
    """
    return dateparse.parse_datetime(text)



@register.filter(name='percent')
@stringfilter
def percent(decimal):
    """
    Outputs the number converted into a float and multiplied by 100.
    """
    return float(decimal) * 100


@register.inclusion_tag('youtube/tagtemplate/test.html')
def show_progress(number):
    """
    Outputs the progressbar in html
    """
    return {'number': number}

@register.inclusion_tag('youtube/tagtemplate/searchform.html', takes_context=True)
def get_search(context):
    """
    Outputs the search form in html
    
    """
    return context