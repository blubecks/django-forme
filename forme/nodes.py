from django import template


class FormeNode(template.Node):
    def __init__(self, tag_name, target, action, nodelist):
        pass