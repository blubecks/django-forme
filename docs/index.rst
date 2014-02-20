Django Forme
============

Contents:

.. toctree::
   :maxdepth: 2

   tags

What's this
===========

``django-forme`` is set of template tags allowing to customize django form's
output. The key idea is that most of customization should be done in template,
not in form definition. It also implements form styles which defines
default form output based on used template (eg. bootstrap_, foundation_, etc.)

.. _bootstrap: http://getbootstrap.com/
.. _foundation: http://foundation.zurb.com/

Working draft
=============

Below are examples showing the planned functionality of app.

.. highlight:: django

* Render ``form`` using default template::

   {% forme form %}

* Render multiple forms (``user_form``, ``profile_form``)::

   {% forme user_form profile_form %}

* Replace template for single field::

   {% forme form replace %}
     {% field "password" using %}
       <input name="{{ field.html_name }}" id="{{ field.html_id }}"
              type="text" value="{{ field.value }}" />
     {% endfield %}
   {% endforme %}

* Override order of fields::

   {% forme form replace %}
     {% field "password" %}
     {% field "username" %}
   {% endforme %}

* Split fields into fieldsets::

   {% forme form replace %}
     <div class="column-left">
       {% fieldset "username email" %}
     </div>
     <div class="column-right">
       {% fieldset "password password1" %}
     </div>
   {% endforme %}

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

