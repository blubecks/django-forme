# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple
from contextlib import contextmanager

from django.utils.encoding import python_2_unicode_compatible


@contextmanager
def update_context(context, push):
    context.update(push)
    yield
    context.pop()


@python_2_unicode_compatible
class Label(namedtuple('LabelDict', 'id label tag')):
    def __str__(self):
        return self.tag

    @classmethod
    def create(cls, field):
        return cls(id=field.id_for_label,
                   label=field.label,
                   tag=field.label_tag())
