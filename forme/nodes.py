# coding: utf-8
from __future__ import unicode_literals

from django import template


class FormeNode(template.Node):
    pass


class FieldsetNode(template.Node):
    pass


class RowNode(template.Node):
    pass


class LabelNode(template.Node):
    pass


class FieldNode(template.Node):
    pass


class HiddenFieldsNode(template.Node):
    pass


class ErrorsNode(template.Node):
    pass


class FieldErrorsNode(template.Node):
    pass


node_classes = {
    'forme': FormeNode,
    'fieldset': FieldsetNode,
    'row': RowNode,
    'label': LabelNode,
    'field': FieldNode,
    'hiddenfields': HiddenFieldsNode,
    'errors': ErrorsNode,
    'fielderrors': FieldErrorsNode,
    }


def node_factory(tag_name, *args, **kwargs):
    try:
        return node_classes[tag_name](*args, **kwargs)
    except KeyError:
        raise KeyError('Missing node class mapping for tag name {}'
                       .format(tag_name))
