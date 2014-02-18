# coding: utf-8
from __future__ import unicode_literals

from django.template import Template, loader
from django.utils.functional import SimpleLazyObject

from forme import settings
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

    return forme_node[0].templates


def preload_styles(styles_config=None):
    if not styles_config:
        styles_config = settings.FORME_STYLES

    # Replace when Py2.6 won't be supported
    # return {name: load_style(tmpl) for name, tmpl in styles_config.items()}
    styles = {}
    for name, tmpl in styles_config.items():
        styles[name] = SimpleLazyObject(lambda: load_style(tmpl))
    return styles


def get_default_style(styles_config=None):
    if not styles_config:
        styles_config = styles
    return styles_config[settings.FORME_DEFAULT_STYLE]


# Needs to be lazy object since template tags aren't loaded yet.
styles = preload_styles()
