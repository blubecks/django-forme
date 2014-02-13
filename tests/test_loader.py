# coding: utf-8
from __future__ import unicode_literals

import pytest
from django.template import Template

from forme.exceptions import FormeInvalidTemplate
from forme.nodes import FormeNode
from forme.loader import load_style


def test_load_style():
    template_string = '''
        {% load forme %}
        {% forme form %}
    '''
    template = Template(template_string)
    style = load_style(template)

    assert isinstance(style, FormeNode)


def test_load_style_multiple_tags():
    template_string = '''
        {% load forme %}
        {% forme form %}
        {% forme another_form %}
    '''
    template = Template(template_string)

    with pytest.raises(FormeInvalidTemplate):
        load_style(template)


def test_load_style_missing_tag():
    template = Template('{% load forme %}')

    with pytest.raises(FormeInvalidTemplate):
        load_style(template)
