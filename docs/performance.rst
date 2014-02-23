Performance
===========

Profiling tests are disabled by default. To run them use::

  $ py.test -m profiling -s

Testing of first two working templates revealed that parsing is about 40x slower,
but rendering is only 1.7x slower which is acceptable, since most production
settings uses template caching.

======  ========  =========
Engine  Parsing   Rendering
======  ========  =========
django  0.094 ms  0.636 ms
forme   3.029 ms  1.077 ms
======  ========  =========

Just informative
================

Comparison above is simple guess. Tested django template is basic ``{{ form }}``
which has almost zero parsing time. Also rendering isn't done by template engine
but directly in ``Form`` class. Sometimes it doesn't produce the same result
either. It's only informative comparison and check that there's no severe
performance overhead.
