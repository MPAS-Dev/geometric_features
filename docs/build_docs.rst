.. _build_docs:

Building the Documentation
==========================

If you add a new capability to ``geometric_features``, it should also be
documented under the ``docs`` directory.  After making changes, it is useful to
do a local build of the docs.

First, make sure to install ``conda-build`` and update ``conda`` in you
``base`` conda environment.  Then, from your ``base`` conda environment, run
the following:

.. code-block:: bash

    # remove any packages you've previously built
    rm -rf ~/miniconda3/conda-bld

    # test building the docs
    conda remove -y --all -n geometric_features_docs
    conda build -m ci/python3.8.yaml recipe
    conda create -y -n geometric_features_docs --use-local python=3.8 \
         geometric_features sphinx sphinx_rtd_theme m2r
    conda activate geometric_features_docs
    cd docs
    make clean
    make html

Finally, you can find the test build in ``_build/html/index.html``.