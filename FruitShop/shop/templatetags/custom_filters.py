"""
Make custom filters for template.
"""

from django import template
import ast

register = template.Library()

@register.filter
def multiply(value, args):
    return value * args

@register.filter
def literal_eval(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value