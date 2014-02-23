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
