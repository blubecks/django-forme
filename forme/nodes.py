# coding: utf-8
from __future__ import unicode_literals

from django import template


class FormeNodeBase(template.Node):
    def __init__(self, target, action, nodelist):
        self.target = target
        self.action = action
        self.nodelist = nodelist

    def render(self, context):
        pass


class FormeNode(FormeNodeBase):
    pass


class FieldsetNode(FormeNodeBase):
    pass


class RowNode(FormeNodeBase):
    pass


class LabelNode(FormeNodeBase):
    pass


class FieldNode(FormeNodeBase):
    pass


class HiddenFieldsNode(FormeNodeBase):
    pass


class ErrorsNode(FormeNodeBase):
    pass


class FieldErrorsNode(FormeNodeBase):
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
        raise KeyError('Missing node class mapping for tag name {name}'
                       .format(name=tag_name))
