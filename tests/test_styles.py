# coding: utf-8
from __future__ import unicode_literals
import pytest
from django import template

from forme import styles


def test_indexing():
    style = styles.Style()
    style['forme'] = 'Foo'
    style['forme', 'test'] = 'Bar'
    assert style['forme', styles.Default] == style['forme']
    assert style['forme', 'invalid key'] == style['forme']
    assert style['forme'] != ['forme', 'test']

    with pytest.raises(KeyError):
        assert style['invalid tag']


def test_ellipsis():
    style = styles.Style()
    style['forme'] = 'Foo'
    style['forme', 'test'] = 'Bar'
    style['forme', 'py'] = 'Fubar'
    assert len(style['forme', :]) == 3

    del style['forme', 'py']
    assert len(style['forme', :]) == 2

    del style['forme', :]
    assert 'forme' not in style


class TestVariableKey:
    def test_variable_key(self):
        var = styles.VariableKey(template.Variable("foo"))
        unresolved_hash = hash(var)
        assert var == template.Variable("foo")

        var.resolve(template.Context({"foo": "bar"}))
        assert var == "bar"
        assert hash(var) == unresolved_hash

    def test_key_dict(self):
        var = styles.VariableKey(template.Variable("foo"))
        test_dict = styles.VariableDict()
        test_dict[var] = 'Template'
        assert var in test_dict
        assert "bar" not in test_dict

        var.resolve(template.Context({"foo": "bar"}))
        assert var in test_dict
        assert "bar" in test_dict



