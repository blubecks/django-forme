Tutorial
========

The aim of ``django-forme`` is to allow customization of form rendering in
templates rather than in ``forms.py`` (or other Python source file). Define
default templates using your css framework markup and only alter rendering of
those fields which need special markup.

Getting started
---------------

1. Install ``django-forme`` using pip:

.. code-block:: shell

    pip install django-forme

2. Add ``forme`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'forme',
    )

3. Load ``forme`` tags in template:

.. code-block:: html+django

    {% load forme %}

Basic example
-------------

Suppose we have following login form:

.. code-block:: python

    class LoginForm(forms.Form):
        username = forms.CharField()
        password = forms.CharField(widget=forms.PasswordInput)


The most trivial use case is rendering whole form using default template.
Instead of writing ``{{ form }}`` in template, we use ``forme`` tag:

.. code-block:: html+django

    {% forme form %}

Result would be:

.. code-block:: html

    <label for="id_username">Username</label>
    <input type="text" name="username" id="id_username">
    <label for="id_password">Password</label>
    <input type="password" name="password" id="id_password">

We can specify default template to render our form using **template** keyword:

.. code-block:: html+django

    {% forme form template="bootstrap" %}

.. code-block:: html

    <div class="form-group">
        <label for="id_username">Username</label>
        <input type="text" class="form-control" id="id_username" name="username">
    </div>
    <div class="form-group">
        <label for="id_password">Password</label>
        <input type="password" class="form-control" id="id_password" name="password">
    </div>

… and that is basically all we can do with ``forme`` tag only. More real use
cases come when we introduce other template tags.

``forme`` tags hierarchy
------------------------

Forms in general are structured in hierarchy:

.. code-block:: html

    <form>
        <hidden fields>
        <non-field errors>
        <fieldset>
            <field>
                <label>
                <input>
                <field errors>
            </field>
        </fieldset>
    </form>

Field errors and non-field errors are relevant for bound forms only. Grouping
fields into fieldsets is optional. This structure represents also ``forme`` tags
hierarchy with corresponding tags:

    ================        ====================
    Element                 ``forme`` tag
    ================        ====================
    form                    ``{% forme %}``
    hidden fields           ``{% hiddenfields %}``
    non-field errors        ``{% nonfielderrors %}``
    fieldset                ``{% fieldset %}``
    field                   ``{% field %}``
    label                   ``{% label %}``
    input                   ``{% input %}``
    field errors            ``{% errors %}``
    ================        ====================

Each tag can be written either as `paired` or `unpaired` one depending on context.

Usage of these tags will be discussed in following sections. This definition
was mentioned to clarify meaning and structure of `forme` tags.

Use or replace
--------------

Consider following example:

.. code-block:: html+django

    {% forme form replace %}
        {% input "password" using %}
            <input class="password" type="password" name="{{ field.name }}" id="{{ field.id }}" />
        {% endinput %}
    {% endforme %}

and the result:

.. code-block:: html

    <label for="id_username">Username</label>
    <input type="text" name="username" id="id_username" />
    <label for="id_password">Password</label>
    <input class="password" type="password" name="password" id="id_password" />

``forme`` tag contains new keyword **replace**. It says: "**Replace** parts
of default template with following templates". It also makes ``forme`` tag
paired one ending with ``{% endforme %}``. Everything between will be considered
as an form element template.

The first (and only) tag inside is input *password*. This tag contains **using**
keyword which says: "**Use** this html code as an template to render input."

In other words: ``forme`` tag will render two fields, *username* and *password*.
*Username* will render label and input using default templates, but *password*
will render label using default template and input using template specified
inside ``input "password"`` tag.
