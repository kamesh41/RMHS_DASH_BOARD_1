from django import template
from itertools import zip_longest

register = template.Library()

@register.filter
def zip_longest_filter(a, b):
    """
    Custom template filter that zips two lists together using itertools.zip_longest.
    Usage: {{ list1|zip_longest:list2 }}
    """
    if isinstance(b, str):
        b = b.split(',')
    return zip_longest(a, b)

@register.filter
def split(value, delimiter=','):
    """
    Custom template filter that splits a string by a delimiter.
    Usage: {{ string|split:"," }}
    """
    return value.split(delimiter) 