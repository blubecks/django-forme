# coding: utf-8
from __future__ import unicode_literals
import copy

import itertools as I
import mock
import pytest
from django import forms
from django import template

from forme import nodes
from forme.parser import FormeParser
from forme.nodes import FormeNode


def tag2nodes(template_string):
    tmpl = template.Template('{% load forme %}' + template_string)
    valid = lambda node: isinstance(node, FormeNode.all_forme_nodes)
    return list(filter(valid, tmpl.nodelist))


def pytest_generate_tests(metafunc):
    if not metafunc.cls:
        return

    if metafunc.cls.__name__ == 'TestChildNodes':
        # called once per each test function
        funcarglist = metafunc.cls().params[metafunc.function.__name__]
        metafunc.parametrize('template_string', funcarglist, ids=funcarglist)


def test_node_factory():
    default_node_args = ('default', 'default', template.NodeList())
    # All valid tags should return Node subclass
    for tag in FormeParser.valid_tags:
        node = nodes.node_factory(tag, *default_node_args)
        assert tag in nodes.node_classes
        assert tag == node.tag_name
        assert isinstance(node,
                          template.Node)

    # Unknown tag
    with pytest.raises(KeyError):
        nodes.node_factory('42_fish')


class TestChildNodes:
    tags = ("field errors label row fieldset"
            " nonfielderrors hiddenfields".split())

    nodes_tag_map = dict(zip(nodes.node_classes.values(),
                             nodes.node_classes.keys()))

    def top_template(self, string):
        return ("{{% load forme %}}{{% forme using %}}{string}{{% endforme %}}"
                .format(string=string))

    def tag_template(self, tag, string=''):
        return ("{{% {tag} using %}}{string}{{% end{tag} %}}"
                .format(tag=tag, string=string))

    def valid_tags(self, tag):
        return [self.nodes_tag_map[node] for node in
                nodes.node_classes[tag].valid_child_nodes]

    def invalid_tags(self, tag):
        return set(self.tags) - set(self.valid_tags(tag))

    @property
    def params(self):
        valid_templates = []
        invalid_templates = []

        for tag in self.tags:
            # invalid_templates = []
            valid_templates.append(self.tag_template(tag))
            for valid in self.valid_tags(tag):
                valid_templates.append(
                    self.tag_template(tag, self.tag_template(valid)))

            for invalid in self.invalid_tags(tag):
                invalid_templates.append(
                    self.tag_template(tag, self.tag_template(invalid)))

        return {
            'test_valid': valid_templates,
            'test_invalid': invalid_templates,
        }

    def test_valid(self, template_string):
        tmpl = self.top_template(template_string)
        try:
            template.Template(tmpl)
        except template.TemplateSyntaxError as e:
            pytest.fail("Should be valid template: {0}."
                        " Exception was {1}.".format(tmpl, e))

    def test_invalid(self, template_string):
        tmpl = self.top_template(template_string)
        try:
            template.Template(tmpl)
        except template.TemplateSyntaxError:
            pass
        else:
            pytest.fail("Shouldn't be valid template: {0}".format(tmpl))


class TestNodeTemplates:
    def test_empty_templates(self):
        tmpl = '{% forme using %}{% endforme %}'
        node = tag2nodes(tmpl)[0]
        assert list(node.templates.keys()) == ['forme']

    def test_default_field_template(self):
        tmpl = '{% forme using %}{% field using %}{% endfield %}{% endforme %}'
        forme = tag2nodes(tmpl)[0]
        # Template for field...
        assert 'field' in forme.templates
        # Default for all fields.
        assert '' in forme.templates['field']

        # Traverse to field node and check parent
        field = forme.templates['field']['']
        assert field.parent == forme

    def test_target_field_template(self):
        tmpl = ('{% forme using %}{% field "username" using %}'
                '{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert 'field' in forme.templates
        assert '"username"' in forme.templates['field']

    def test_template_order_preserved(self):
        tmpl = ('{% forme using %}{% field "username" using %}{% endfield %}'
                '{% field "password" using %}{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert ['"username"', '"password"'] \
                == list(forme.templates['field'].keys())

        tmpl = ('{% forme using %}{% field "password" using %}{% endfield %}'
                '{% field "username" using %}{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert ['"password"', '"username"'] \
                == list(forme.templates['field'].keys())

    def test_override_parent_template(self):
        tmpl = ('{% forme using %}'
                '{% field using %}Parent{% endfield %}'
                '{% fieldset using %}{% field using %}Child{% endfield %}'
                '{% endfieldset %}{% endforme %}')

        forme = tag2nodes(tmpl)[0]
        fieldset = forme.templates['fieldset']['']

        # Get content of first node (TextNode) in field's nodelist
        text_node = lambda node: node.templates['field'][''].nodelist[0].s
        assert text_node(forme) == 'Parent'
        assert text_node(fieldset) == 'Child'


class TestNodeRender:
    @pytest.fixture
    def field(self):
        field = forms.forms.BoundField(forms.Form(), forms.Field(), 'field')
        return field

    @pytest.fixture
    def render_mock(self, request):
        m = mock.Mock()
        p = mock.patch.object(nodes.FormeNodeBase, 'render', m)
        p.start()
        request.addfinalizer(p.stop)
        return self.copy_call_args(m)

    def copy_call_args(self, mock):
        """
        Recipe from:
        http://docs.python.org/dev/library/unittest.mock-examples.html#coping-with-mutable-arguments

        """
        new_mock = mock.Mock()

        def side_effect(*args, **kwargs):
            args = copy.deepcopy(args)
            kwargs = copy.deepcopy(kwargs)
            new_mock(*args, **kwargs)
            return mock.DEFAULT
        mock.side_effect = side_effect
        return new_mock

    def flatten(self, context):
        flat = {}
        for ctx in context:
            flat.update(ctx)
        return flat

    def test_fielderrors_no_errors(self, field):
        node = nodes.ErrorsNode('errors', '', '')
        assert node.render(template.Context({'field': field})) == ''

    def test_fielderrors(self, field, render_mock):
        field.form._errors = {'field': 'test_errors'}
        node = nodes.ErrorsNode('errors', '', '')
        node.render(template.Context({'field': field}))

        context = self.flatten(render_mock.call_args[0][0])
        assert 'field' in context
        assert 'errors' in context
        assert context['errors'] == context['field'].errors

    def test_label(self, field, render_mock):
        node = nodes.LabelNode('label', '', '')
        node.render(template.Context({'field': field}))

        context = self.flatten(render_mock.call_args[0][0])
        assert 'field' in context
        assert 'label' in context

        field = context['field']
        label = context['label']
        assert label['id'] == field.id_for_label
        assert label['label'] == field.label
        assert label['tag'] == field.label_tag()

    def test_hiddenfields_no_fields(self):
        node = nodes.HiddenFieldsNode('hiddenfields', '', '')
        assert node.render(template.Context({'form': forms.Form()})) == ''

    def test_errors_no_errors(self):
        node = nodes.NonFieldErrorsNode('nonfielderrors', '', '')
        assert node.render(template.Context({'form': forms.Form()})) == ''
