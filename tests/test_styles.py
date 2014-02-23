# coding: utf-8
from __future__ import unicode_literals
import pytest

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

