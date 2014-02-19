# coding: utf-8
from __future__ import unicode_literals
from collections import defaultdict
import copy

from django import template
from django.utils.datastructures import SortedDict


class FormeNodeBase(template.Node):
    direct_child_nodes = ()
    valid_child_nodes = ()
    all_forme_nodes = ()

    def __init__(self, tag_name, target, action=None, nodelist=None):
        self.tag_name = tag_name
        self.target = target
        self.action = action or 'default'
        self.nodelist = nodelist or template.NodeList()

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
        self.remove_template_nodes()

    def get_direct_child_nodes_by_type(self, nodetype):
        valid = lambda node: isinstance(node, nodetype)
        return [node for node in self.nodelist if valid(node)]

    def is_template(self, node=None):
        if not node:
            node = self

        direct = self.direct_child_nodes or self.valid_child_nodes
        template_nodes = tuple(set(self.all_forme_nodes) - set(direct))

        is_template = isinstance(node, tuple(template_nodes))
        is_default = isinstance(node, self.all_forme_nodes) and node.default
        return is_template or is_default

    def remove_template_nodes(self):
        self.nodelist = template.NodeList([node for node in self.nodelist
                                           if not self.is_template(node)])

    def render(self, context):
        if self.nodelist:
            return self.nodelist.render(context)
        else:
            target = self.target[0] in self.templates[self.tag_name] or ''
            return self.templates[self.tag_name][target].render(context)

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
                    templates[node.tag_name][target.var] = node
            # Define default template.
            else:
                templates[node.tag_name][''] = node

        # Set missing child templates from self
        for node in child_nodes:
            node.set_parent(self)

        self.templates.update(templates)


class FieldNode(FormeNodeBase):
    """
    Renders single field. It doesn't push any variables into context because
    'field' variable is already pushed by row node.

    """


class ErrorsNode(FormeNodeBase):
    """
    Renders field errors, if any. It pushes 'errors' variable into context
    which is alias to field.errors.

    """
    def render(self, context):
        errors = getattr(context['field'], 'errors', None)
        if not errors:
            return ''

        context.update({'errors': errors})
        output = super(ErrorsNode, self).render(context)
        context.pop()
        return output


class LabelNode(FormeNodeBase):
    """
    Renders field's label. it pushes 'label' variable into context which is
    a dict containing:
        id: alias for field.id_for_label
        label: alias for field.label
        tag: alias for field.label_tag

    """
    # It's a bit tricky, will be added in future.
    # valid_child_nodes = (FieldNode, ErrorsNode)

    def render(self, context):
        field = context['field']
        context.update({
            'label': {
                'id': field.id_for_label,
                'label': field.label,
                'tag': field.label_tag(),
            },
        })
        output = super(LabelNode, self).render(context)
        context.pop()
        return output


class RowNode(FormeNodeBase):
    """
    Renders single row which usualy consists of field errors, label and field.
    It adds 'field' variable into context as reference to rendered field.

    """
    valid_child_nodes = (FieldNode, LabelNode, ErrorsNode)


class FieldsetNode(FormeNodeBase):
    """
    Renders list of row nodes. Adds 'fields' to context which is list of
    rendered field objects.

    """
    direct_child_nodes = (RowNode,)
    valid_child_nodes = direct_child_nodes + RowNode.valid_child_nodes


class HiddenFieldsNode(FormeNodeBase):
    """
    Renders all form's hidden fields, if any. Pushes 'hidden_fields' variable
    into context as an alias for form.hidden_fields().

    """
    def render(self, context):
        hidden_fields = context['form'].hidden_fields()
        if not hidden_fields:
            return ''

        context.update({'hidden_fields': hidden_fields})
        output = super(HiddenFieldsNode, self).render(context)
        context.pop()
        return output


class NonFieldErrorsNode(FormeNodeBase):
    """
    Renders non field errors, if any. It pushes 'non_fields_errors' variable
    into context which is an alias to form.non_fields_errors().

    """
    def render(self, context):
        errors = context['form'].non_field_errors()
        if not errors:
            return ''

        context.update({'non_field_errors': errors})
        output = super(NonFieldErrorsNode, self).render(context)
        context.pop()
        return output


class FormeNode(FormeNodeBase):
    """
    Top level tag to render form. Adds 'form' to context which represent
    rendered form.

    """
    direct_child_nodes = HiddenFieldsNode, NonFieldErrorsNode, FieldsetNode
    valid_child_nodes = direct_child_nodes + FieldsetNode.valid_child_nodes


node_classes = {
    'forme': FormeNode,
    'fieldset': FieldsetNode,
    'row': RowNode,
    'label': LabelNode,
    'field': FieldNode,
    'hiddenfields': HiddenFieldsNode,
    'nonfielderrors': NonFieldErrorsNode,
    'errors': ErrorsNode,
}
FormeNodeBase.all_forme_nodes = tuple(node_classes.values())


def node_factory(tag_name, *args, **kwargs):
    try:
        return node_classes[tag_name](tag_name, *args, **kwargs)
    except KeyError:
        raise KeyError('Missing node class mapping for tag name {name}'
                       .format(name=tag_name))
