# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple, defaultdict

from django.utils.datastructures import SortedDict

Variant = namedtuple('Variant', 'tag target')


class Default:
    pass


class Style(object):
    def __init__(self):
        self._data = defaultdict(SortedDict)

    def __contains__(self, key):
        key = self._normalize_key(key)
        if isinstance(key.target, slice):
            return key.tag in self._data
        else:
            return key.tag in self._data and key.target in self._data[key.tag]

    def __getitem__(self, key):
        key = self._normalize_key(key)
        if isinstance(key.target, slice):
            return self._data[key.tag]

        variants = self._data[key.tag]
        if key.target != Default and key.target in variants:
            return variants[key.target]
        else:
            return variants[Default]

    def __setitem__(self, key, value):
        key = self._normalize_key(key)
        self._data[key.tag][key.target] = value

    def __delitem__(self, key):
        key = self._normalize_key(key)
        if isinstance(key.target, slice):
            del self._data[key.tag]
        else:
            del self._data[key.tag][key.target]

    @classmethod
    def _normalize_key(cls, key):
        if not isinstance(key, tuple):
            key = (key, Default)
        return Variant(*key)
