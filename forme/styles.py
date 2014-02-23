# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple

Variant = namedtuple('Variant', 'tag target')


class Default:
    pass


class Style(dict):
    def __getitem__(self, key):
        key = self._normalize_key(key)
        try:
            return super(Style, self).__getitem__(key)
        except KeyError:
            pass

        if key.tag != Default:
            alter_key = Variant(key.tag, Default)
            try:
                return super(Style, self).__getitem__(alter_key)
            except KeyError:
                pass

        msg = 'Template for tag {0} is missing.'.format(key.tag)
        raise KeyError(msg)

    def __setitem__(self, key, value):
        key = self._normalize_key(key)
        return super(Style, self).__setitem__(key, value)

    def __delitem__(self, key):
        key = self._normalize_key(key)
        return super(Style, self).__delitem__(key)

    @classmethod
    def _normalize_key(cls, key):
        if not isinstance(key, tuple):
            key = (key, Default)
        return Variant(*key)
