# coding: utf-8
from __future__ import unicode_literals

import glob
import os
import os.path
import sys
import timeit

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


def normalize_text(lines):
    lines = [line.strip() for line in lines.split('\n')]
    return '\n'.join(filter(None, lines))


class TestTemplates:
    def load_context(self, case):
        temp_ = __import__('{0}.context'.format(case),
                           fromlist=['skip', 'context'], level=0)
        ctx = template.Context(temp_.context)
        skip = getattr(temp_, 'skip', False)
        if skip:
            pytest.skip()
        return ctx

    def load_template(self, template_name):
        with open(template_name, 'r') as file_:
            return template.Template(file_.read())

    def test_template(self, case, template_name):
        """
        Render template blocks "template" and "expected" and compare them.

        """
        ctx = self.load_context(case)
        tmpl = self.load_template(template_name)

        from django.template.loader_tags import BlockNode
        nodes = tmpl.nodelist.get_nodes_by_type(BlockNode)
        params = dict([(node.name, normalize_text(node.nodelist.render(ctx)))
                       for node in nodes])

        assert params['template'] == params['expected']

    @pytest.mark.profiling
    def test_profilling(self, case, template_name):
        ctx = self.load_context(case)

        n = 1000

        django_parse = lambda: template.Template('{{ form }}')
        forme_parse = lambda: self.load_template(template_name)

        times_parse = {
            'django': timeit.Timer(django_parse).timeit(n),
            'forme': timeit.Timer(forme_parse).timeit(n),
        }

        django_tmpl = django_parse()
        tmpl = forme_parse()

        from django.template.loader_tags import BlockNode
        nodes = tmpl.nodelist.get_nodes_by_type(BlockNode)
        params = dict([(node.name, node.nodelist)
                       for node in nodes])

        forme_tmpl = params['template']

        django_render = lambda: django_tmpl.render(ctx)
        forme_render = lambda: forme_tmpl.render(ctx)

        times_render = {
            'django': timeit.Timer(django_render).timeit(n),
            'forme': timeit.Timer(forme_render).timeit(n),
        }

        slower = lambda d: d['forme'] / d['django']

        print('-' * 40)
        print('Template: {0}/{1}'.format(case, os.path.basename(template_name)))
        print('--- Parsing (Slower {0:.1f}x)'.format(slower(times_parse)))
        for key, value in times_parse.items():
            print('{0:^8} {1:.3f} ms'.format(key, value))
        print('--- Rendering (Slower {0:.1f}x)'.format(slower(times_render)))
        for key, value in times_render.items():
            print('{0:^8} {1:.3f} ms'.format(key, value))
