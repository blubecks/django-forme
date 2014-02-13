# coding: utf-8
from __future__ import unicode_literals, absolute_import

from django import template

from forme.parser import FormeParser

register = template.Library()


def do_forme_parser(parser, tokens):
    return FormeParser(parser, tokens).parse()

for tag in FormeParser.valid_tags:
    register.tag(tag, do_forme_parser)
