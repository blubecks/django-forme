Performance
===========

Profiling tests are disabled by default. To run them use::

  $ py.test -m profiling -s

Testing of first two working templates revealed that parsing is about 30x slower,
but rendering is only 1.7x slower which is acceptable, since most production
settings uses template caching.

======  ========  =========
Engine  Parsing   Rendering
======  ========  =========
django  0.094 ms  0.636 ms
forme   3.029 ms  1.077 ms
======  ========  =========
