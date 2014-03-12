# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple, defaultdict

from django import template

Variant = namedtuple('Variant', 'tag target')


class Default: pass


class VariableDict(dict):
    def resolve(self, context):
        for variable, tmpl in self.items():
            if isinstance(variable, template.Variable):
                self[variable.resolve(context)] = tmpl


class Style(object):
    def __init__(self, template=None):
        self._data = defaultdict(VariableDict)
        self.template = template

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

    def __repr__(self):
        return "<Style {0}".format(self._data)

    def render(self, context):
        if self.template:
            return self.template.render(context)

    @classmethod
    def _normalize_key(cls, key):
        if not isinstance(key, tuple):
            key = (key, Default)
        else:
            tag, target = key
            if not target:
                target = Default
            key = (tag, target)
        return Variant(*key)

    def resolve(self, tag, context):
        self._data[tag].resolve(context)
