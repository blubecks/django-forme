# coding: utf-8
from __future__ import unicode_literals
from collections import defaultdict
import copy

from django import template
from django.utils.datastructures import SortedDict


class FormeNodeBase(template.Node):
    valid_child_nodes = ()
    all_forme_nodes = ()

    def __init__(self, tag_name, target, action, nodelist):
        self.tag_name = tag_name
        self.target = target
        self.action = action
        self.nodelist = nodelist

        # Nodes without targets are default templates.
        self.default = not target

        self.parent = None
        if self.tag_name == 'forme' and not self.default:
            from forme import loader
            self.templates = loader.get_default_style()
        else:
            # Will be set from parent node or default style
            self.templates = defaultdict(SortedDict)

        child_nodes = self.validate_child_nodes()
        self.update_templates(child_nodes)

    def get_direct_child_nodes_by_type(self, nodetype):
        valid = lambda node: isinstance(node, nodetype)
        return [node for node in self.nodelist if valid(node)]

    def set_parent(self, parent):
        self.parent = parent

        # Copy parent templates and override with all defined templates
        templates = copy.deepcopy(parent.templates)
        templates.update(self.templates)
        self.templates = templates

    def validate_child_nodes(self):
        child_nodes = self.get_direct_child_nodes_by_type(self.all_forme_nodes)

        if not child_nodes:
            return []

        if self.valid_child_nodes:
            invalid = lambda node: not isinstance(node, self.valid_child_nodes)
            invalid_nodes = filter(invalid, child_nodes)
        else:
            # No child nodes are allowed
            invalid_nodes = child_nodes

        if any(invalid_nodes):
            msg = ("Node {0} can\'t contain following nodes: {1}"
                   .format(self.__class__, invalid_nodes))
            raise template.TemplateSyntaxError(msg)

        return child_nodes

    def update_templates(self, child_nodes):
        templates = defaultdict(SortedDict)
        for node in child_nodes:
            # Define templates for all targets.
            if node.target:
                for target in node.target:
                    templates[node.tag_name][target] = node
            # Define default template.
            else:
                templates[node.tag_name][''] = node

        # Set missing child templates from self
        for node in child_nodes:
            node.set_parent(self)

        self.templates.update(templates)

class FieldNode(FormeNodeBase):
    pass


class FieldErrorsNode(FormeNodeBase):
    pass


class LabelNode(FormeNodeBase):
    valid_child_nodes = (FieldNode, FieldErrorsNode)


class RowNode(FormeNodeBase):
    valid_child_nodes = (FieldNode, LabelNode, FieldErrorsNode)


class FieldsetNode(FormeNodeBase):
    valid_child_nodes = (RowNode,) + RowNode.valid_child_nodes


class HiddenFieldsNode(FormeNodeBase):
    pass


class ErrorsNode(FormeNodeBase):
    pass


class FormeNode(FormeNodeBase):
    valid_child_nodes = ((HiddenFieldsNode, ErrorsNode, FieldsetNode)
                         + FieldsetNode.valid_child_nodes)


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
FormeNodeBase.all_forme_nodes = tuple(node_classes.values())


def node_factory(tag_name, *args, **kwargs):
    try:
        return node_classes[tag_name](tag_name, *args, **kwargs)
    except KeyError:
        raise KeyError('Missing node class mapping for tag name {name}'
                       .format(name=tag_name))
