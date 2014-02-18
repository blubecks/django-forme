# coding: utf-8
from __future__ import unicode_literals

import pytest
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
    default_node_args = ('default', 'default', [])
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
    tags = ("field fielderrors label row fieldset"
            " errors hiddenfields".split())

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
        assert node.templates == {}

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

