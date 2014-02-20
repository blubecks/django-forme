# coding: utf-8
from __future__ import unicode_literals
from collections import defaultdict

from django import template
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe


class FormeNodeBase(template.Node):
    tag_name = None

    direct_child_nodes = ()
    valid_child_nodes = ()
    all_forme_nodes = ()

    def __init__(self, target=None, action=None, nodelist=None):
        self.target = target
        self.action = action or 'default'
        self.nodelist = nodelist or template.NodeList()

        self.parent = None
        if self.tag_name == 'forme' and self.target:
            # Rendering forme, load default style
            from forme import loader
            templates = loader.get_default_style()

            # Workaround for unsubscriptable SimpleLazyObject in Dj1.5
            if hasattr(templates, '_wrapped'):
                bool(templates)
                self.templates = templates._wrapped
            else:
                self.templates = templates
        else:
            # Defining forme style.
            # TODO: Allow extending existing styles
            # (eg. {% forme style "bare" using %})
            self.templates = defaultdict(SortedDict)

        self.validate_child_nodes()
        self.update_templates()

        if self.tag_name == 'forme':
            if self.action == 'using':
                self.templates['forme'][''] = self.nodelist

            # Trigger nodes cleanup
            self.clean_nodelist()

    def clean_nodelist(self):
        if self.action == 'replace':
            self.nodelist = template.NodeList()
        else:
            self.nodelist[:] = template.NodeList(
                [node for node in self.nodelist if not self.is_template(node)])

        for node in self.get_direct_child_nodes():
            node.clean_nodelist()

    def get_direct_child_nodes(self, nodetype=None):
        if not nodetype:
            nodetype = self.valid_child_nodes
        return (node for node in self.nodelist if isinstance(node, nodetype))

    def get_template(self, tag, target, context):
        self.templates[tag] = self.resolve_template_keys(
            self.templates[tag], context)

        try:
            tmpl = self.templates[tag][target]
        except KeyError:
            if self.parent:
                tmpl = self.parent.get_template(tag, target, context)
            else:
                tmpl = None
        return tmpl

    def is_template(self, node):
        if not node:
            node = self

        direct_nodes = self.direct_child_nodes or self.valid_child_nodes
        indirect_nodes = tuple(set(self.all_forme_nodes) - set(direct_nodes))
        return isinstance(node, indirect_nodes)

    def render(self, context):
        if self.nodelist:
            return self.nodelist.render(context)
        else:
            possible_targets = ['']
            if self.tag_name != 'forme':
                if isinstance(self.target, list):
                    target = self.target[0] if len(self.target) else None
                else:
                    target = self.target
                possible_targets.insert(0, target)

            for possibility in possible_targets:
                tmpl = self.get_template(self.tag_name, possibility, context)
                if tmpl:
                    return tmpl.render(context)

            msg = ('Missing template for tag {0}'
                   .format(self.tag_name))
            raise template.TemplateSyntaxError(msg)

    def resolve_template_keys(self, templates, context):
        for target, tmpl in templates.items():
            if isinstance(target, template.Variable):
                del templates[target]
                templates[target.resolve(context)] = tmpl
        return templates

    def update_templates(self):
        for node in self.get_direct_child_nodes(self.all_forme_nodes):
            node.parent = self

            if node.action != 'using':
                continue

            # Define templates for all targets.
            if node.target:
                for target in node.target:
                    self.templates[node.tag_name][target] = node.nodelist
            # Define default template.
            elif node.action == 'using':
                self.templates[node.tag_name][''] = node.nodelist

    def validate_child_nodes(self):
        child_nodes = self.get_direct_child_nodes(self.all_forme_nodes)

        if not child_nodes:
            return []

        if self.valid_child_nodes:
            invalid_nodes = (node for node in child_nodes
                             if not isinstance(node, self.valid_child_nodes))
        else:
            # No child nodes are allowed
            invalid_nodes = child_nodes

        if any(invalid_nodes):
            msg = ("Node {0} can\'t contain following nodes: {1}"
                   .format(self.__class__, invalid_nodes))
            raise template.TemplateSyntaxError(msg)


class FieldNode(FormeNodeBase):
    """
    Renders single field. It doesn't push any variables into context because
    'field' variable is already pushed by row node.

    """
    tag_name = 'field'

    def __repr__(self):
        return '<Field node>'

    def render(self, context):
        self.target = context['field'].name
        return super(FieldNode, self).render(context)


class ErrorsNode(FormeNodeBase):
    """
    Renders field errors, if any. It pushes 'errors' variable into context
    which is alias to field.errors.

    """
    tag_name = 'errors'

    def __repr__(self):
        return '<Errors node>'

    def render(self, context):
        errors = getattr(context['field'], 'errors', None)
        if not errors:
            return ''

        self.target = context['field'].name

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
    tag_name = 'label'
    # It's a bit tricky, will be added in future.
    # valid_child_nodes = (FieldNode, ErrorsNode)

    def __repr__(self):
        return '<Label node>'

    def render(self, context):
        field = context['field']

        self.target = field.name

        context.update({
            'label': {
                'id': field.id_for_label,
                'label': field.label,
                'tag': mark_safe(field.label_tag()),
            },
        })
        output = super(LabelNode, self).render(context)
        context.pop()
        return output


class RowNode(FormeNodeBase):
    """
    Renders single row which usualy consists of field errors, label and field.
    It adds 'field' variable into context as reference to rendered field or
    'fields' variable if row contains more than one field. Template itself
    is responsible for looping over fields..

    """
    tag_name = 'row'
    valid_child_nodes = (FieldNode, LabelNode, ErrorsNode)

    def __repr__(self):
        return '<Row node>'

    def render(self, context):
        form = context['form']

        output = ''
        if not self.target:
            fields = context['fieldset_fields']
            for field in fields:
                context.update({'field': field})
                output += super(RowNode, self).render(context)
                context.pop()
        else:
            fields = [form[field.resolve(context)] for field in self.target]

            if len(fields) > 1:
                context_variable = 'fields'
            else:
                context_variable = 'field'

            context.update({context_variable: fields})
            output += super(RowNode, self).render(context)
            context.pop()

        return output


class FieldsetNode(FormeNodeBase):
    """
    Renders list of row nodes. Adds 'fieldset_fields' to context which is list
    of rendered field objects.

    """
    tag_name = 'fieldset'
    direct_child_nodes = (RowNode,)
    valid_child_nodes = direct_child_nodes + RowNode.valid_child_nodes

    def __repr__(self):
        return '<Fieldset node>'

    def render(self, context):
        form = context['form']
        fields = [form[field.resolve(context)] for field in self.target]

        if not any(fields):
            fields = list(form)

        context.update({'fieldset_fields': fields})
        output = super(FieldsetNode, self).render(context)
        context.pop()

        return output


class HiddenFieldsNode(FormeNodeBase):
    """
    Renders all form's hidden fields, if any. Pushes 'hidden_fields' variable
    into context as an alias for form.hidden_fields().

    """
    tag_name = 'hiddenfields'

    def __repr__(self):
        return '<HiddenFields node>'

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
    tag_name = 'nonfielderrors'

    def __repr__(self):
        return '<NonFieldErrors node>'

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
    tag_name = 'forme'

    direct_child_nodes = HiddenFieldsNode, NonFieldErrorsNode, FieldsetNode
    valid_child_nodes = direct_child_nodes + FieldsetNode.valid_child_nodes

    def __init__(self, target=None, action=None, nodelist=None):
        if not target and not action:
            raise template.TemplateSyntaxError('Missing form parameter.')
        super(FormeNode, self).__init__(target, action, nodelist)

    def __repr__(self):
        return '<Forme node>'

    def render(self, context):
        forms = [form.resolve(context) for form in self.target]
        if not any(forms):
            raise template.TemplateSyntaxError('Need form to render.')
        elif len(self.target) > 1:
            context_variable = 'forms'
        else:
            context_variable = 'form'
            forms = forms[0]

        context.update({context_variable: forms})
        output = super(FormeNode, self).render(context)
        context.pop()

        return output


forme_nodes = (FormeNode, NonFieldErrorsNode, HiddenFieldsNode, FieldsetNode,
               RowNode, ErrorsNode, LabelNode, FieldNode)
tag_map = dict([(node.tag_name, node) for node in forme_nodes])

FormeNodeBase.all_forme_nodes = forme_nodes


def node_factory(tag_name, *args, **kwargs):
    try:
        return tag_map[tag_name](*args, **kwargs)
    except KeyError:
        raise KeyError('Missing node class mapping for tag name {name}'
                       .format(name=tag_name))
