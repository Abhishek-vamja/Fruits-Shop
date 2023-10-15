"""
Make custom filters for template.
"""

from django import template

register = template.Library()

@register.filter
def multiply(value, args):
    return value * args