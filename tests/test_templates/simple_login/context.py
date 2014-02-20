# coding: utf-8
from __future__ import unicode_literals

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password')

context = {
    'form': LoginForm()
}

skip = False
