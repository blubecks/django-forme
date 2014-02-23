# coding: utf-8
from __future__ import unicode_literals

import pytest
from django import forms
from django import template

from forme.context import Label, update_context


def test_push_context():
    context = template.Context({'field': 'Foo'})
    with update_context(context, {'field': 'Bar'}):
        assert context['field'] == 'Bar'
    assert context['field'] == 'Foo'


class TestLabel:
    @pytest.fixture
    def field(self):
        field = forms.forms.BoundField(forms.Form(), forms.Field(), 'field')
        return field

    def test_label_attributes(self, field):
        label = Label.create(field)
        # Check field attributes mapping
        assert label.id == field.id_for_label
        assert label.label == field.label
        assert label.tag == field.label_tag()

        assert label.id == 'id_field'
        assert label.label == 'Field'

        # Check rendering (mark_safe issues) and check alias
        ctx = template.Context({'label': label})
        rendered = template.Template('{{ label }}').render(ctx)
        rendered_tag = template.Template('{{ label.tag }}').render(ctx)
        assert rendered == rendered_tag == str(label)
