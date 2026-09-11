from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Safely get a value from a dictionary by key."""
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None

@register.filter
def dict_get(dictionary, key):
    """Alias for get_item, more semantic in templates."""
    return get_item(dictionary, key)
