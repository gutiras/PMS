# gantt_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """ Custom filter to get value from dictionary """
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Repeats a string by the given multiplier (value * arg)."""
    return str(value) * int(arg)
