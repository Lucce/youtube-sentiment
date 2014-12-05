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
    Outputs the input text in a readable date format.
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
    Outputs a dictionary with the input as key and a value.
    """
    return {'number': number}