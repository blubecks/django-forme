# coding: utf-8
from __future__ import unicode_literals

import copy
from django import template

from forme.nodes import node_factory, tag_map


class FormeParser(object):
    valid_tags = tag_map.keys()
    common_actions = 'using replace'.split()

    def __init__(self, parser, token):
        self.parser = parser
        self.parts = token.split_contents()
        self.tag_name = self.parts.pop(0)

    @property
    def valid_actions(self):
        actions = self.common_actions

        if self.tag_name == 'field':
            return actions + ['hide']
        else:
            return actions

    def parse(self):
        parts = copy.copy(self.parts)
        action, paired = self.parse_action(parts)
        target = self.parse_target(parts)
        nodelist = self.parse_nodelist() if paired else []

        return node_factory(self.tag_name, target, action, nodelist)

    def parse_action(self, parts):
        try:
            action = parts[-1]
        except IndexError:
            action = 'default'
        else:
            if action in self.valid_actions:
                # Last token is action, remove it
                parts.pop()
            else:
                # Last token is target, action isn't specified
                action = 'default'

        paired = action != 'default'
        return action, paired

    def parse_target(self, parts):
        targets = []
        for part in parts:
            if ' ' in part:
                # Only string can contain a space. Strip quotes, split strings
                # and surround them with quotes so they resolve properly later.
                stripped_parts = part.strip('"\'').split(' ')
                targets.extend('"{0}"'.format(p) for p in stripped_parts)
            else:
                # Either variable or string with single name
                targets.append(part)

        return [template.Variable(target) for target in targets]

    def parse_nodelist(self):
        end_node = 'end' + self.tag_name
        nodelist = self.parser.parse((end_node,))
        self.parser.delete_first_token()
        return nodelist
