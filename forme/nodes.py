# coding: utf-8
from __future__ import unicode_literals

from django import template


class FormeNodeBase(template.Node):
    valid_child_nodes = ()
    all_forme_nodes = ()

    def __init__(self, tag_name, target, action, nodelist):
        self.tag_name = tag_name
        self.target = target
        self.action = action
        self.nodelist = nodelist

        child_nodes = self.validate_child_nodes()

        # Nodes without targets are default templates.
        self.default = not target

    def render(self, context):
        pass

    def validate_child_nodes(self):
        child_nodes = self.get_nodes_by_type(self.all_forme_nodes)
        # First node in list is node itself.
        child_nodes.pop(0)

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
