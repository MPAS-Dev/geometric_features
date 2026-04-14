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
    DOCS_VERSION=test make clean versioned-html

Previewing the Documentation
============================

To preview the documentation locally, open the ``index.html`` file in the
``_build/html/test`` directory with your browser or try:

.. code-block:: bash

   cd _build/html
   python -m http.server 8000

Then, open http://0.0.0.0:8000/test/ in your browser.
