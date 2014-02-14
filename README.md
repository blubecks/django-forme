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
    {% fieldset "username email" %}
    <div class="left-column">
        {{ fieldset_content }}
    </div>
    {% endfieldset %}

    {% fieldset "password password_check" %}
    <div class="right-column">
        {{ fieldset_content }}
    </div>
    {% endfieldset %}
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

These are real-world examples I'm dealing with in one project right now,
but any of existing tools don't allow me to do so.

Working draft of ideas follows:

Rendering using default templates
---------------------------------

Rendering of form using default template:
```html+django

{% load forme %}

{# Default usage, no overrides #}
{% forme form %}

{# Render using default <p>-style #}
{% forme form style p %}

{# Custom style defined on per app or per project basis #}
{% forme form style horizontal %}
```

"Default template" can be overridden on per-app of per-project basis. Planned
templates are 'bootstrap' and 'foundation'.

Overriding of specific parts
----------------------------

General structure of most forms (based od bootstrap and foundation styles) is:

*Form* > *Fieldset* > *Row* > (*Label* + *Field*)

It should be possible to override desired parts using just few lines of code.

In examples below, `<level>` can be substituted with one of `forme`, `fieldset`,
 `row`, `label` or `field`.

Target is `form` to render (eg. `{% forme form %}`) for level `forme`.
For all other levels, its either variable or string of target to render
(eg. `{% field "username" %}`). Multiple values can be specified as single
string separated with spaces (eg. `{% field "username password" %}`).

Three actions are possible:

### 1. Default
 - when no action is specified, it renders target using default templates

```html+django
{% forme form %}
{% fieldset "username email" %}
{% row "down" %}
{% label "rabbit" %}
{% field "finally" %}
```

### 2. `replace`
 - pair tag, ended with `{% end<level> %}` (eg. `{% endfield %}`)
 - only elements specified will be replaced in default template.
 - it can contain other *forme* tags only, no html+django allowed

```html+django
{% forme form replace %}
   {% field "username" %}
   {% field "email" %}

    ...
{% endform %}
```

### 3. `using`
 - also pair tag
 - overrides default template
 - can contain html

```html+django
{% forme form using %}
   <p>Please fill the form bellow.</p>
   {% field "username" %}

   ...
{% endform %}
```

Tags can be nested:
```html+django
{% forme form replace %}
    {% field "username" %}
    {% field "email" using %}
        <p>Valid email please</p>
        <input ...>
    {% endfield %}

    ...
{% endform %}
```

… and so on. Work on progress, ping me if interested, poke me if I'm reinventing
wheel of kick me if you think this approach is totally wrong.


Other apps dealing with forms
=============================

Listed in order I discovered them:

1. [django-crispy-forms](https://github.com/maraujop/django-crispy-forms)
   Most of configuration is done in Layout in python code. Nope.

2. [django-widget-tweaks](https://github.com/kmike/django-widget-tweaks)
   Nice, but it deals mostly with fields.

3. [django-floppyforms](https://github.com/brutasse/django-floppyforms)
   Close, but still there's no simple way to override a tiny bit of form.