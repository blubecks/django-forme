# coding: utf-8
from __future__ import unicode_literals

from django.conf import settings

default = lambda key, value: getattr(settings, key, value)


FORME_STYLES = default('FORME_STYLES', {
    'bare': 'forme/bare.html',
})

FORME_DEFAULT_STYLE = default('FORME_DEFAULT_STYLE', 'bare')
