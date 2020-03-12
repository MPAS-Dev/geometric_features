#!/bin/bash

set -e

source $HOME/miniconda/etc/profile.d/conda.sh
conda activate base
conda build -m "travis_ci/linux_${TRAVIS_JOB_NAME}.yaml" "recipe"

conda create -y -n test --use-local geometric_features pytest sphinx mock \
   sphinx_rtd_theme m2r

conda activate test

if [[ "$TRAVIS_BRANCH" == "master" ]]; then
  export DOCS_VERSION="stable"
elif [ -n "$TRAVIS_TAG" ]; then
  # this is a tag build
  export DOCS_VERSION="$TRAVIS_TAG"
else
  DOCS_VERSION=`python -c "import geometric_features; print(geometric_features.__version__)"`
  export DOCS_VERSION
fi
cd docs || exit 1
make html
