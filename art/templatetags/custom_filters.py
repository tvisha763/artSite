from datetime import datetime
from django import template

register = template.Library()

@register.filter
def convert_str_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date()