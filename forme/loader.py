# coding: utf-8
from __future__ import unicode_literals

from django.template import Template, loader

from forme.exceptions import FormeInvalidTemplate
from forme.nodes import FormeNode


def load_style(template_name):
    # template_name can be either path to template of Template object
    if isinstance(template_name, Template):
        template = template_name
    else:
        template = loader.get_template(template_name)
    forme_node = template.nodelist.get_nodes_by_type(FormeNode)

    if not forme_node:
        raise FormeInvalidTemplate('"forme" tag not found in {tmpl}'
                                   .format(tmpl=template_name))
    if len(forme_node) > 1:
        raise FormeInvalidTemplate(
            'Only one "forme" tag can be present. {count} found in {tmpl}'
            .format(count=len(forme_node), tmpl=template_name))

    forme_node = forme_node[0]

    return forme_node
