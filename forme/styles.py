# coding: utf-8
from __future__ import unicode_literals
from collections import namedtuple, defaultdict

from django import template

Variant = namedtuple('Variant', 'tag target')


class Default: pass
class Unresolved: pass


class VariableKey(object):
    def __init__(self, variable):
        self.variable = variable
        self.resolved = Unresolved

    def resolve(self, context):
        self.resolved = self.variable.resolve(context)

    def __eq__(self, other):
        if isinstance(other, VariableKey):
            if self.resolved is Unresolved:
                return self.variable.var == other.variable.var
            else:
                return self.resolved == other.resolved
        elif isinstance(other, template.Variable):
            return self.variable.var == other.var
        else:
            return self.resolved == other

    def __hash__(self):
        return hash(self.variable)

    def __repr__(self):
        msg = "<VariableKey variable: {0}, resolved: {1}>"
        return msg.format(self.variable, self.resolved)


class VariableDict(dict):
    def __getitem__(self, item):
        try:
            return next(value for key, value in self.items() if key == item)
        except StopIteration:
            raise KeyError(item)

    def __contains__(self, item):
        return any(True for key in self if key == item)

    def resolve(self, context):
        for variable in self.keys():
            if isinstance(variable, VariableKey):
                variable.resolve(context)


class Style(object):
    def __init__(self):
        self._data = defaultdict(VariableDict)

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

    @classmethod
    def _normalize_key(cls, key):
        if not isinstance(key, tuple):
            key = (key, Default)
        elif isinstance(key[1], template.Variable):
            key = (key[0], VariableKey(key[1]))
        return Variant(*key)

    def resolve(self, tag, context):
        self._data[tag].resolve(context)
