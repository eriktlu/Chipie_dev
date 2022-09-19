from django import template

from decimal import *

from decimal import Decimal

register = template.Library()

@register.simple_tag()
def divide(a, b, *args, **kwargs):
    # you would need to do any localization of the result here
    # getcontext().prec = 2
    return Decimal(str(a))/Decimal(str(b))