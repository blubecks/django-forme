# coding: utf-8
from __future__ import unicode_literals

import glob
import os
import os.path
import sys

from django import template
import pytest

test_dir = os.path.join(os.path.dirname(__file__), 'test_templates')
sys.path.insert(0, test_dir)


def get_cases():
    return [dir_ for dir_ in os.listdir(test_dir)
            if os.path.isdir(os.path.join(test_dir, dir_))]


def get_templates(case):
    template_dir = os.path.join(test_dir, case, 'templates')
    return glob.glob('{0}/test_*.html'.format(template_dir))


def pytest_generate_tests(metafunc):
    args, ids = [], []

    for case in get_cases():
        for template_name in get_templates(case):
            args.append((case, template_name))
            ids.append('/'.join([case, os.path.basename(template_name)]))

    metafunc.parametrize('case,template_name', args, ids=ids)


def test_template(case, template_name):
    """
    Render template blocks "template" and "expected" and compare them.

    """
    temp_ = __import__('{}.forms'.format(case),  fromlist=['skip', 'context'], level=0)
    ctx = temp_.context
    skip = getattr(temp_, 'skip', False)
    if skip:
        pytest.skip()

    with open(template_name, 'r') as file_:
        tmpl = template.Template(file_.read())

    from django.template.loader_tags import BlockNode
    nodes = tmpl.nodelist.get_nodes_by_type(BlockNode)
    params = dict([(node.name, node.nodelist) for node in nodes])

    assert params['template'].render(ctx) == params['expected'].render(ctx)
