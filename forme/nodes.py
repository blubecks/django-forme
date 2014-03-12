# coding: utf-8
from __future__ import unicode_literals

from django import template

from forme.context import Label, update_context
from forme.styles import Style


class FormeNodeBase(template.Node):
    tag_name = None

    child_nodes = ()
    template_nodes = ()
    all_forme_nodes = ()

    def __init__(self, target=None, action=None, nodelist=None):
        self.target = target
        self.action = action or 'default'
        self.nodelist = nodelist or template.NodeList()

        self.parent = None
        if self.tag_name == 'forme' and self.target:
            # Rendering forme, load default style
            from forme import loader
            styles = loader.get_default_style()

            # Workaround for unsubscriptable SimpleLazyObject in Dj1.5
            if hasattr(styles, '_wrapped'):
                bool(styles)
                self.styles = styles._wrapped
            else:
                self.styles = styles
        else:
            self.styles = Style()

        self.validate_child_nodes()
        self.update_styles()

        if self.tag_name == 'forme':
            if self.action == 'using':
                self.styles['forme'] = Style(template=self.nodelist)

            # Trigger nodes cleanup
            self.clean_nodelist()

    def clean_nodelist(self):
        if self.action == 'replace':
            self.nodelist[:] = []
        else:
            self.nodelist[:] = [node for node in self.nodelist
                                if not self.is_template(node)]

        for node in self.get_direct_child_nodes():
            node.clean_nodelist()

    def get_direct_child_nodes(self, nodetype=None):
        if not nodetype:
            nodetype = self.template_nodes
        return (node for node in self.nodelist if isinstance(node, nodetype))

    def get_template(self, tag, target, context):
        self.styles.resolve(tag, context)

        try:
            tmpl = self.styles[tag, target]
        except KeyError:
            if self.parent:
                tmpl = self.parent.get_template(tag, target, context)
            else:
                tmpl = None
        return tmpl

    def is_template(self, node):
        if not node:
            node = self

        return isinstance(node, self.template_nodes)

    def render(self, context):
        if self.nodelist:
            tmpl = self.nodelist
        else:
            if isinstance(self.target, list):
                target = self.target[0] if len(self.target) else None
            else:
                target = self.target

            tmpl = self.get_template(self.tag_name, target, context)

        if tmpl:
            with update_context(context, {'forme_style': self.styles}):
                return tmpl.render(context)
        else:
            msg = ('Missing template for tag {0}'
                   .format(self.tag_name))
            raise template.TemplateSyntaxError(msg)

    def update_styles(self):
        for node in self.get_direct_child_nodes(self.all_forme_nodes):
            node.parent = self

            if node.action != 'using':
                continue

            tmpl = Style(template=node.nodelist)
            # Define templates for all targets.
            if node.target:
                for target in node.target:
                    self.styles[node.tag_name, target] = tmpl
            # Define default template.
            elif node.action == 'using':
                self.styles[node.tag_name] = tmpl

    def validate_child_nodes(self):
        child_nodes = self.get_direct_child_nodes(self.all_forme_nodes)

        if not child_nodes:
            return []

        valid_nodes = self.template_nodes + self.child_nodes
        if valid_nodes:
            invalid_nodes = (node for node in child_nodes
                             if not isinstance(node, valid_nodes))
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

        with update_context(context, {'errors': errors}):
            return super(ErrorsNode, self).render(context)


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

        with update_context(context, {'label': Label.create(field)}):
            return super(LabelNode, self).render(context)


class RowNode(FormeNodeBase):
    """
    Renders single row which usualy consists of field errors, label and field.
    It adds 'field' variable into context as reference to rendered field or
    'fields' variable if row contains more than one field. Template itself
    is responsible for looping over fields..

    """
    tag_name = 'row'
    child_nodes = FieldNode, LabelNode, ErrorsNode

    def __repr__(self):
        return '<Row node>'

    def render(self, context):
        form = context['form']

        output = ''
        if not self.target:
            fields = context['fieldset_fields']
            for field in fields:
                with update_context(context, {'field': field}):
                    output += super(RowNode, self).render(context)
        else:
            fields = [form[field.resolve(context)] for field in self.target]

            if len(fields) > 1:
                context_variable = 'fields'
            else:
                context_variable = 'field'

            with update_context(context, {context_variable: fields}):
                output += super(RowNode, self).render(context)

        return output


class FieldsetNode(FormeNodeBase):
    """
    Renders list of row nodes. Adds 'fieldset_fields' to context which is list
    of rendered field objects.

    """
    tag_name = 'fieldset'
    child_nodes = (RowNode,)
    template_nodes = RowNode.child_nodes + RowNode.template_nodes

    def __repr__(self):
        return '<Fieldset node>'

    def render(self, context):
        form = context['form']
        fields = [form[field.resolve(context)] for field in self.target]

        if not any(fields):
            fields = list(form)

        with update_context(context, {'fieldset_fields': fields}):
            return super(FieldsetNode, self).render(context)


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

        with update_context(context, {'hidden_fields': hidden_fields}):
            return super(HiddenFieldsNode, self).render(context)


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

        with update_context(context, {'non_field_errors': errors}):
            return super(NonFieldErrorsNode, self).render(context)


class FormeNode(FormeNodeBase):
    """
    Top level tag to render form. Adds 'form' to context which represent
    rendered form.

    """
    tag_name = 'forme'

    child_nodes = HiddenFieldsNode, NonFieldErrorsNode, FieldsetNode
    template_nodes = FieldsetNode.child_nodes + FieldsetNode.template_nodes

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

        with update_context(context, {context_variable: forms}):
            return super(FormeNode, self).render(context)


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
