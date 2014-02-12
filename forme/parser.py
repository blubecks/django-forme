# coding: utf-8
from __future__ import unicode_literals

import copy
from django import template

from forme.nodes import FormeNode


class FormeParser(object):
    def __init__(self, parser, token):
        self.parser = parser
        self.parts = token.split_contents()
        self.tag_name = self.parts.pop()

    def parse(self):
        parts = copy.copy(self.parts)
        action, paired = self.parse_action(parts)
        target = self.parse_target(parts)

        nodelist = self.parse_nodelist() if paired else []

        return FormeNode(self.tag_name, target, action, nodelist)

    def parse_action(self, parts):
        try:
            action = parts[-1]
        except ValueError:
            action = 'default'
        else:
            if action in ['using', 'replace']:
                # Last token is action, remove it
                parts.pop()
            else:
                # Last token is target, action isn't specified
                action = 'default'

        paired = action != 'default'
        return action, paired

    def parse_target(self, parts):
        target = []
        for part in parts:
            target.extend(part.split(' '))

        if not target:
            msg = "Missing %s target.".format(self.tag_name)
            raise template.TemplateSyntaxError(msg)

        return target

    def parse_nodelist(self):
        end_node = ''.join(['end', self.tag_name])
        nodelist = self.parser.parse((end_node,))
        self.parser.delete_frist_node()
        return nodelist
