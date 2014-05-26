# coding: utf-8
from __future__ import unicode_literals
import copy

import mock
import pytest
from django import forms
from django import template

from forme import nodes
from forme.context import Label
from forme.parser import FormeParser
from forme.nodes import FormeNode
from forme.styles import Default


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
    default_node_args = ('default',)
    # All valid tags should return Node subclass
    for tag in FormeParser.valid_tags:
        assert tag in nodes.tag_map

        node = nodes.node_factory(tag, *default_node_args)
        assert tag == node.tag_name
        assert isinstance(node, template.Node)

    # Unknown tag
    with pytest.raises(KeyError):
        nodes.node_factory('42_fish')


def test_forme_requires_target_or_action():
    with pytest.raises(template.TemplateSyntaxError):
        nodes.node_factory('forme')

    try:
        nodes.node_factory('forme', action='default')
    except template.TemplateSyntaxError:
        pytest.fail('forme tag with action and without target failed.')

    try:
        nodes.node_factory('forme', target=template.Variable('form'))
    except template.TemplateSyntaxError:
        pytest.fail('forme tag without action and with target failed.')


class TestChildNodes:
    tags = ("field errors label row fieldset"
            " nonfielderrors hiddenfields".split())

    nodes_tag_map = dict(zip(nodes.tag_map.values(),
                             nodes.tag_map.keys()))

    def top_template(self, string):
        return ("{{% load forme %}}{{% forme using %}}{string}{{% endforme %}}"
                .format(string=string))

    def tag_template(self, tag, string=''):
        return ("{{% {tag} using %}}{string}{{% end{tag} %}}"
                .format(tag=tag, string=string))

    def valid_tags(self, tag):
        node = nodes.tag_map[tag]
        child_nodes = node.template_nodes + node.child_nodes
        return [self.nodes_tag_map[node] for node in child_nodes]

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
        assert 'forme' in node.styles

    def test_default_field_template(self):
        tmpl = '{% forme using %}{% field using %}{% endfield %}{% endforme %}'
        forme = tag2nodes(tmpl)[0]
        # Template for field...
        assert 'field' in forme.styles
        # Default for all fields.
        assert 'field', Default in forme.styles

    def test_target_field_template(self):
        tmpl = ('{% forme using %}{% field "username" using %}'
                '{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert 'field', '"username"' in forme.styles

    def test_template_order_preserved(self):
        pytest.skip('Ordering will be reimplemented.')
        tmpl = ('{% forme using %}{% field "username" using %}{% endfield %}'
                '{% field "password" using %}{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert ['"username"', '"password"']\
                == [var.var for var in forme.styles['field'].keys()]

        tmpl = ('{% forme using %}{% field "password" using %}{% endfield %}'
                '{% field "username" using %}{% endfield %}{% endforme %}')
        forme = tag2nodes(tmpl)[0]
        assert ['"password"', '"username"'] \
                == [var.var for var in forme.styles['field'].keys()]

    def test_override_parent_template(self):
        tmpl = ('{% forme using %}'
                '{% field using %}Parent{% endfield %}'
                '{% fieldset using %}{% field using %}Child{% endfield %}'
                '{% endfieldset %}{% endforme %}')

        forme = tag2nodes(tmpl)[0]
        fieldset = forme.nodelist.get_nodes_by_type(nodes.FieldsetNode)[0]

        # Get content of first node (TextNode) in field's nodelist
        text_node = lambda node: node.styles['field'].template[0].s
        assert text_node(forme) == 'Parent'
        assert text_node(fieldset) == 'Child'


class TestNodeBase(object):
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


class TestFieldErrorsNode(TestNodeBase):
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


class TestLabelNode(TestNodeBase):
    def test_label(self, field, render_mock):
        node = nodes.LabelNode('label', '', '')
        node.render(template.Context({'field': field}))

        context = self.flatten(render_mock.call_args[0][0])
        assert 'field' in context
        assert 'label' in context

        field = context['field']
        label = context['label']
        assert label == Label.create(field)


class TestHiddenFieldsNode(TestNodeBase):
    def test_hiddenfields_no_fields(self):
        node = nodes.HiddenFieldsNode('hiddenfields', '', '')
        assert node.render(template.Context({'form': forms.Form()})) == ''


class TestErrorsNoErrors(TestNodeBase):
    def test_errors_no_errors(self):
        node = nodes.NonFieldErrorsNode('nonfielderrors', '', '')
        assert node.render(template.Context({'form': forms.Form()})) == ''
