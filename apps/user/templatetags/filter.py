from django.template import Library

register = Library()

@register.filter
def sadd(value, arg):
    try:
        return round(value + arg, 2)
    except (ValueError, TypeError):
        try:
            return value + arg
        except Exception:
            return ''
