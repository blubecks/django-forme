[![Build Status](https://travis-ci.org/elvard/django-forme.png?branch=master)](https://travis-ci.org/elvard/django-forme)

Django forme
============

Django forms for template designers… and for me!

Goal
----

I want to do this:

```html+django
{% forme my_form %}
```

most of the time and get html output according to Bootstrap. Yes I know about
an app which has `|as_bootstrap` filter. But that's not enough.

Sometimes, I want to add simple suffix to some fields:

```html+django
{% forme my_form using %}
    {% field "value" suffix %}
        <span class="add-on">CZK</span>
    {% endfield %}
{% endforme %}
```

but still get the same default html template as before with input-addon
after field "value".

Occasionaly I want to split my form into two columns:

```html+django
{% forme my_form using %}
    <div class="left-column">
        {% fieldset "username email" %}
    </div>

    <div class="right-column">
        {% fieldset "password password_check" %}
    </div>
{% endforme %}
```

and still render fields and labels using default template.

Rarely I would like to change order of fields or hide some of them (even when
I process them) without messing with form definition:

```html+django
{% forme my_form using %}
    {% field "first third second" %}
    {% field "user" hide %} {# I'll take it from request.user and validate it #}
{% endforme %}
```

… and so on. Work on progress, ping me if interested, poke me if I'm reinventing
wheel of kick me if you think this approach is totally wrong.

These are real-world examples I'm dealing with in one project right now,
but any of existing tools don't allow me to do so.

Other apps dealing with forms
=============================

Listed in order I discovered them:

1. [django-crispy-forms](https://github.com/maraujop/django-crispy-forms)
   Most of configuration is done in Layout in python code. Nope.

2. [django-widget-tweaks](https://github.com/kmike/django-widget-tweaks)
   Nice, but it deals mostly with fields.

3. [django-floppyforms](https://github.com/brutasse/django-floppyforms)
   Close, but still there's no simple way to override a tiny bit of form.