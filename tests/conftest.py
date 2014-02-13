# coding: utf-8
from __future__ import unicode_literals

import pytest
from mock import patch, Mock

from django.template import Token, TOKEN_BLOCK

from forme.parser import FormeParser


@pytest.fixture
def node_mock(request):
    m = Mock()
    p = patch('forme.parser.node_factory', m)
    p.start()
    request.addfinalizer(p.stop)
    return m


@pytest.fixture
def forme():
    return FormeParser([], Token(TOKEN_BLOCK, 'tag'))

