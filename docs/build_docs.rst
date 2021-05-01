.. _build_docs:

Building the Documentation
==========================

If you add a new capability to ``geometric_features``, it should also be
documented under the ``docs`` directory.  After making changes, it is useful to
do a local build of the docs.

First, set up the development environment as described in :ref:`quick_start`.
Then, run:

.. code-block:: bash

    cd docs
    make clean
    make html

You can find the test build in ``_build/html/index.html``.